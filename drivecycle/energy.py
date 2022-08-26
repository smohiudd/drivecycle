import numpy as np
from scipy import interpolate
from drivecycle import utils
import inspect
from typing import List, Any, Optional
import numpy.typing as npt


def energy_model(traj: List[float],
                  elv: Optional[List[List[float]]] = None,
                  capacity: int = 300, #kWh
                  power_aux:float = 0.0, #auxiliary loads kWh
                  **kwargs: str) -> npt.NDArray[Any]:
    """Battery State of Charge (SoC) modelling.

    Args:
        traj (list): time, velocity, distance list
        elv (list): elevation along the route
        capacity (int): batter capacity (kWh)
        power_aux (float): auxiliary load on the vehicle (kWh)

    Returns:
        list: (n,5) numpy array of time, velocity, distance, cumulative power, SoC
    """

    data = np.c_[traj, np.zeros((len(traj), 2))]  # Power, SoC
    data[0,4]=1
    alpha = None

    if elv is not None:
        x = [i[0] for i in elv]
        y = [i[1] for i in elv]
        elv_f = interpolate.interp1d(x, y)

    for i, (prev, curr) in enumerate(utils.pairwise(traj)):

        t0, v0, d0 = prev
        t1, v1, d1 = curr

        accel = (v1 - v0) / (t1 - t0)

        if v1 == 0:
            data[i + 1, 3:5] = data[i, 3:5]
        else:
            if elv is not None:
                try:
                    alpha = (elv_f(d1) - elv_f(d0)) / (d1 - d0)
                except ValueError: # d1 or d0 is outside elv range, don't include alpha in calcluation
                    alpha = None
                
            # determine tractive force
            trac_force_kwargs = list(
                inspect.signature(tractive_force).parameters)
            force = tractive_force(
                v1,
                accel,
                alpha=alpha,
                **{
                    i: kwargs[i]  # type: ignore
                    for i in kwargs if i in trac_force_kwargs
                },
            )

            # power supplied to or from the battery
            batt_power_kwargs = list(
                inspect.signature(battery_power).parameters)
            power_batt = battery_power(
                v1, 
                force, 
                **{
                    i: kwargs[i]  # type: ignore
                    for i in kwargs if i in batt_power_kwargs
                },
            )

            # Include accessory/auxiliary power
            power = (power_batt/1000) + power_aux # Total power in kW

            Einst = power * ((t1-t0)/3600) # Instantaneous energy in kWh

            #print(f"Power: {power}, Einst: {Einst}, SOC: {Einst/capacity}")
            
            data[i + 1, 3] = data[i,3] + Einst
            data[i + 1, 4] = data[i,4] - (Einst/capacity)

    return data

def battery_model(traj: List[float],
                  elv: Optional[List[List[float]]] = None,
                  num_cells: int = 2000,
                  capacity: int = 75,
                  k: float = 1.0,
                  battery_type: str = "LI-ION",
                  power_aux: float = 0.0,
                  **kwargs: str) -> npt.NDArray[Any]:
    """Battery Depth of Discharge (DoD) modelling.

    Battery depth of discharge modelling using calculations for 
    current draw from the battery.

    Args:
        traj (list): time, velocity, distance list
        elv (list): elevation along the route
        num_cells (int): number of battery cells
        capacity (int): amp hour capacity of cell, 1C
        k (float): peuker coefficient
        battery_type (str): battery chemical type

    Returns:
        list: (n,6) numpy array of time, velocity, distance, power, current, DoD

    """

    data = np.c_[traj, np.zeros((len(traj), 3))]  # Power, Cr, DoD
    r_in = (0.022 / capacity) * num_cells  # Internal resistance
    peu_cap = (np.power((capacity / 1), k)) * 1
    alpha = None

    if elv is not None:
        x = [i[0] for i in elv]
        y = [i[1] for i in elv]
        elv_f = interpolate.interp1d(x, y)

    for i, (prev, curr) in enumerate(utils.pairwise(traj)):

        t0, v0, d0 = prev
        t1, v1, d1 = curr

        accel = (v1 - v0) / (t1 - t0)

        if v1 == 0:
            data[i + 1, 3:6] = data[i, 3:6]
        else:

            if elv is not None:
                alpha = (elv_f(d1) - elv_f(d0)) / (d1 - d0)

            trac_force_kwargs = list(
                inspect.signature(tractive_force).parameters)
            force = tractive_force(
                v1,
                accel,
                alpha=alpha,
                **{
                    i: kwargs[i]  # type: ignore
                    for i in kwargs if i in trac_force_kwargs
                },
            )

            batt_power_kwargs = list(
                inspect.signature(battery_power).parameters)
            power_batt = battery_power(
                v1,
                force,
                **{
                    i: kwargs[i]  # type: ignore
                    for i in kwargs if i in batt_power_kwargs
                })

            data[i + 1, 3] = power_batt+power_aux

            # determine open circuit voltage given battery type and number of cells
            voltage = open_circuit_voltage(data[i, 5],
                                           type=battery_type) * num_cells
                                           
            if power_batt > 0:
                a = np.power(voltage, 2) - (4 * r_in * power_batt)
                assert a > 0, "Cannot determine current, insufficient total voltage."

                # Current drawn from the battery
                batt_current = (voltage - np.sqrt(a)) / (2 * r_in)
                data[i + 1,
                     4] = data[i, 4] + ((batt_current*(t1-t0)) / 3600)
            elif power_batt == 0:
                batt_current = 0
            elif power_batt < 0:
                # Regenerative braking double the internal resistance.
                a = np.power(voltage, 2) + (4 * 1.0 * r_in * -power_batt)
                assert a > 0, "Cannot determine current, insufficient total voltage."

                # Current drawn from the battery
                batt_current = (-voltage + np.sqrt(a)) / (2 * 1.0 * r_in)
                data[i + 1, 4] = data[i, 4] - ((batt_current*(t1-t0)) / 3600)

            # assuming battery cells are in series therefor capacity is same as input
            data[i + 1, 5] = data[i + 1, 4] / peu_cap 

    return data  # type: ignore


def battery_power(
    v: float,
    force: float, # tractive force in N
    gear_ratio: float = 4.66,
    radius_wheel: float = 0.5, # wheel radius in m
    regen_ratio: float = 0.5, # proportion of braking forcing to use for regen
    trans_eff: float = 0.95,  # transmission efficiency
    motor_eff: float = 0.90, # motor efficiency
    pow_conv_eff: float = 0.95, # power converter efficiency
    # ki: float = 0.01,  # iron losses
    # kw: float = 0.000005,  # windage losses
    # kc: float = 0.3,  # copper losses
    # con_l: int = 600,
) -> float:
    """Battery power modelling.

    Calculate power supplied from or transfer to the battery. 

    Args:
        v (float): velocity (m/s)
        force (float): tractive force (N)
        gear_ratio (float): gear ratio
        radius_wheel (float): dynamic radius of tires (m)
        regen_ratio (float): proportion of braking forcing to use for regen
        trans_eff (float): transmission efficiency
        motor_eff (float): motor efficiency
        pow_conv_eff (float): power converter efficiency
    Returns:
        float: Power supplied from the battery (excluding accessor power)

    """
    
    if force<0:
        force = force*regen_ratio

    torque_wheel = force * radius_wheel #torque at the wheel

    torque_motor = torque_wheel/(gear_ratio* trans_eff) # torque at the motor

    omega_wheel = v/radius_wheel #angular velocity of the wheel
    omega_motor = omega_wheel * gear_ratio #angular velocity of motor

    power = (torque_motor * omega_motor)/(motor_eff*pow_conv_eff) #Power in Watts

    return power

    # TODO include formula for motor efficiency

    # if v==0:
    #     pmot_in=0
    # elif v>0:
    #     if force<0:
    #         force = regen_ratio * force * g_eff
    #     elif force >=0:
    #         force = force / g_eff

    #     torque = (force * rw)/gr
    #     omega = (gr * v)/rw

        # if torque > 0:
        #     eff_mot = (torque * omega) / ((torque * omega) +
        #                                   (np.power(torque, 2) * kc) +
        #                                   (omega * ki) +
        #                                   ((np.power(omega, 3) * kw) + con_l))
        # elif torque < 0:
        #     eff_mot = (-torque * omega) / ((-torque * omega) +
        #                                    (np.power(torque, 2) * kc) +
        #                                    (omega * ki) +
        #                                    ((np.power(omega, 3) * kw) + con_l))

        # if force >= 0:
        #     pmot_in = (force *v) / 0.85
        # elif force < 0:
        #     pmot_in =(force *v) * 0.85

    # return pmot_in

def tractive_force(
    v: float,
    accel: float,
    alpha: Optional[float] = None,
    ch: float = 1.2,
    m: float = 12000.0,
    air_density: float = 1.2,
    cw: float = 1.17,
    area: float = 10.0,
) -> Any:
    """Tractive force.

    Calculation of the force propelling the vehicles forward transferred through the drive wheels.

    Args:
        v (float): velocity (m/s)
        accel (float): acceleration (m/s^2)
        alpha (float): elevation grade
        ch (float): rolling resistance coefficient
        m (float): mass (kg)
        air_density (float): air density
        cw (float): air density coefficient
        area (float): frontal area of vehicle

    Returns:
        float: total tractive force (N)

    """
    g = 9.81

    f = (0.0041 + 0.000041 * v * 2.24) * ch
    roll_resist_force = m * f * g

    if air_density:
        aero_drag_force = 0.5 * air_density * cw * area * np.power(v, 2)
    else:
        aero_drag_force = 0.0

    if alpha:
        hill_climb_force = m * g * np.sin(alpha)
    else:
        hill_climb_force = 0.0

    accel_force = m * accel

    return roll_resist_force + aero_drag_force + hill_climb_force + accel_force


def open_circuit_voltage(x: float, type: str = "LA") -> float:
    """Open Circiut Voltage.

    Li-ion open circuit volage as found in:

    Zhang R. et. al. (2018). A Study on Open Circuit Voltage and State of Charge
    Characterization of High Capacity Lithium-Ion Battery Under Different Temperature.
    Energies 2018, 1, 2408.

    Args:
        x (float): Depth of Discharge
        type (str): battery chemistry type

    Returns:
        float: open circuit voltage


    """

    # TODO: Remove LA and NC battey type since not common anymore

    voltage = 0.0
    
    if type == "LA":
        voltage = (2.15 - ((2.15 - 2.00) * x))
    elif type == "NC":
        voltage = (-8.2816 * (np.power(x, 7)) + 23.5749 *
                               (np.power(x, 6)) - 30 *
                               (np.power(x, 5)) + 23.7053 *
                               (np.power(x, 4)) - 12.5877 * (np.power(x, 3)) +
                               4.1315 * x * x - 0.8658 * x + 1.37)
    elif type == "LI-ION":
        s = 1 - x
        voltage = 0.76 * np.power(s, 5) - 3.72 * np.power(
            s, 4) + 6.15 * np.power(s, 3) - 3.64 * np.power(
                s, 2) + 1.26 * np.power(s, 1) + 3.24

    return voltage
