import numpy as np
from scipy import interpolate
from drivecycle import utils
import inspect
from typing import List, Any, Optional
import numpy.typing as npt


def battery_model(traj: List[float],
                  elv: Optional[List[List[float]]] = None,
                  num_cells: int = 200,
                  capacity: int = 50,
                  k: float = 1.045,
                  battery_type: str = "LI-ION",
                  **kwargs: str) -> npt.NDArray[Any]:
    """Battery Depth of Discharge modelling.

    Model battery depth of discharge 

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
    # peu_cap = (np.power((capacity / 10), k)) * 10
    peu_cap = capacity
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

            p_te = (force * v1)  # Watts
            data[i + 1, 3] = p_te

            batt_power_kwargs = list(
                inspect.signature(battery_power).parameters)
            p_batt = battery_power(
                v1,
                p_te,
                **{
                    i: kwargs[i]  # type: ignore
                    for i in kwargs if i in batt_power_kwargs
                })
            # p_batt = battery_power(v1, p_te, **batt_power)

            voltage = open_circuit_voltage(data[i, 5],
                                           num_cells,
                                           type=battery_type)

            if p_batt > 0:
                a = np.power(voltage, 2) - (4 * r_in * p_batt)
                assert a > 0, "Cannot determine current, insufficient total voltage."

                batt_current = (voltage - np.sqrt(a)) / (2 * r_in)
                data[i + 1,
                     4] = data[i, 4] + (np.power(batt_current, k) / 3600)
            elif p_batt == 0:
                batt_current = 0
            elif p_batt < 0:
                # Regenerative braking double the internal resistance.
                a = np.power(voltage, 2) - (4 * 2 * r_in * -p_batt)
                assert a > 0, "Cannot determine current, insufficient total voltage."

                batt_current = (-voltage + np.sqrt(a)) / (2 * 2 * r_in)
                data[i + 1, 4] = data[i, 4] - (batt_current / 3600)

            data[i + 1, 5] = data[i + 1, 4] / peu_cap

    return data  # type: ignore


def battery_power(
    v: float,
    p_te: float,
    p_ac: float = 0.0,
    g_ratio: float = 37.0,  # gear ratio G/r,
    regen_ratio: float = 0.5,
    g_eff: float = 0.95,  # transmission efficiency
    ki: float = 0.01,  # iron losses
    kw: float = 0.000005,  # windage losses
    kc: float = 0.3,  # copper losses
    con_l: int = 600,
) -> float:
    """Battery power modelling.

    Extended description...

    Args:
        v (float): velocity (m/s)
        p_te (float): total power needed for motion (Watts)
        p_ac (float): power needed for accessories (Watts)
        g_ratio (float): gear ratio (G/r)
        regen_ratio (float): regeneration ratio from breaking
        g_eff (float): transmission efficiency
        ki (float): iron losses
        kw (float): windage losses
        kw (float): copper losses
        con_l (float): coefficient

    Returns:
        float: Power supplied from the batter

    """

    omega = g_ratio * v

    if omega == 0:
        p_te = 0.0
        pmot_in = 0.0
        torque = 0.0
        eff_mot = 0.5
    elif omega > 0:
        if p_te < 0:
            p_te = regen_ratio * p_te

        if p_te >= 0:
            pmot_out = p_te / g_eff
        elif p_te < 0:
            pmot_out = p_te * g_eff

        torque = pmot_out / omega

        if torque > 0:
            eff_mot = (torque * omega) / ((torque * omega) +
                                          (np.power(torque, 2) * kc) +
                                          (omega * ki) +
                                          ((np.power(omega, 3) * kw) + con_l))
        elif torque < 0:
            eff_mot = (-torque * omega) / ((-torque * omega) +
                                           (np.power(torque, 2) * kc) +
                                           (omega * ki) +
                                           ((np.power(omega, 3) * kw) + con_l))

        if pmot_out >= 0:
            pmot_in = pmot_out / eff_mot
        elif pmot_out < 0:
            pmot_in = pmot_out * eff_mot

    return pmot_in + p_ac


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

    Extended description...

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


def open_circuit_voltage(x: float, num_cells: int, type: str = "LA") -> float:
    """Open Circiut Voltage.

    Extended description...

    Args:
        x (float): Depth of Discharge
        num_cells (int): num of battery cells
        type (str): battery chemistry type

    Returns:
        float: open circuit voltage

    """

    voltage = 0.0

    if type == "LA":
        voltage = (2.15 - ((2.15 - 2.00) * x)) * num_cells
    elif type == "NC":
        voltage = num_cells * (-8.2816 * (np.power(x, 7)) + 23.5749 *
                               (np.power(x, 6)) - 30 *
                               (np.power(x, 5)) + 23.7053 *
                               (np.power(x, 4)) - 12.5877 * (np.power(x, 3)) +
                               4.1315 * x * x - 0.8658 * x + 1.37)
    elif type == "LI-ION":
        s = 1 - x
        voltage = 0.76 * np.power(s, 5) - 3.72 * np.power(
            s, 4) + 6.15 * np.power(s, 3) - 3.64 * np.power(
                s, 2) + 1.26 * np.power(s, 1) + 3.24

    return voltage * num_cells
