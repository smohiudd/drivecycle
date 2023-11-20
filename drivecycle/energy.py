import inspect
from typing import Any, List, Optional

import numpy as np
import numpy.typing as npt
import pandas as pd
from scipy import interpolate


def energy_model(
    traj: List[float],
    elv: Optional[List[List[float]]] = None,
    capacity: int = 300,  # kWh
    power_aux: float = 0.0,  # auxiliary loads kWh
    **kwargs: str,
) -> npt.NDArray[Any]:
    """Battery State of Charge (SoC) modelling.

    Args:
        traj (list): time, velocity, distance list
        elv (list): elevation along the route
        capacity (int): batter capacity (kWh)
        power_aux (float): auxiliary load on the vehicle (kWh)

    Returns:
        list: (n,5) numpy array of time, velocity, distance, cumulative power, SoC
    """

    elv_f = None
    if elv is not None:
        elv_array = np.array(elv)
        elv_f = interpolate.interp1d(elv_array[:, 0], elv_array[:, 1])

    df = pd.DataFrame(traj, columns=["t0", "v0", "d0"])
    df["t1"] = df["t0"].shift(-1, fill_value=0)
    df["v1"] = df["v0"].shift(-1, fill_value=0)
    df["d1"] = df["d0"].shift(-1, fill_value=0)

    df["alpha"] = df.apply(lambda x: _get_elv(x, elv_f), axis=1)

    df["accel"] = df.apply(lambda x: (x["v1"] - x["v0"]) / (x["t1"] - x["t0"]), axis=1)
    df["Einst"] = df.apply(lambda x: _get_Einst(x, power_aux, **kwargs), axis=1)
    df["power"] = df["Einst"].cumsum()
    df["soc"] = (df["Einst"] / -capacity).cumsum() * 100

    df = df[["t1", "v1", "d1", "power", "soc"]][:-1]  # remove last row because of shift

    return np.vstack((np.zeros((1, 5)), df.to_numpy()))  # add row to zeros in first row


def battery_power(
    v: float,
    force: float,  # tractive force in N
    gear_ratio: float = 4.66,
    radius_wheel: float = 0.5,  # wheel radius in m
    regen_ratio: float = 0.5,  # proportion of braking forcing to use for regen
    trans_eff: float = 0.95,  # transmission efficiency
    motor_eff: float = 0.90,  # motor efficiency
    pow_conv_eff: float = 0.95,  # power converter efficiency
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

    if force < 0:
        force = force * regen_ratio

    torque_wheel = force * radius_wheel  # torque at the wheel

    torque_motor = torque_wheel / (gear_ratio * trans_eff)  # torque at the motor

    omega_wheel = v / radius_wheel  # angular velocity of the wheel
    omega_motor = omega_wheel * gear_ratio  # angular velocity of motor

    power = (torque_motor * omega_motor) / (motor_eff * pow_conv_eff)  # Power in Watts

    return power


def tractive_force(
    v: float,
    accel: float,
    alpha: float = 0,
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

    hill_climb_force = m * g * np.sin(alpha)

    accel_force = m * accel

    return roll_resist_force + aero_drag_force + hill_climb_force + accel_force


def _get_Einst(x, power_aux, **kwargs):
    trac_force_kwargs = list(inspect.signature(tractive_force).parameters)
    force = tractive_force(
        x["v1"],
        x["accel"],
        alpha=x["alpha"],
        **{i: kwargs[i] for i in kwargs if i in trac_force_kwargs},  # type: ignore
    )

    batt_power_kwargs = list(inspect.signature(battery_power).parameters)
    power_batt = battery_power(
        x["v1"],
        force,
        **{i: kwargs[i] for i in kwargs if i in batt_power_kwargs},  # type: ignore
    )

    power = (power_batt / 1000) + power_aux  # Total power in kW
    return power * ((x["t1"] - x["t0"]) / 3600)


def _get_elv(x, elv_f):
    if elv_f is not None:
        d = x["d1"] - x["d0"]
        try:
            if d != 0:
                return (elv_f(x["d1"]) - elv_f(x["d0"])) / d
            else:
                return 0
        except ValueError:
            return 0
    else:
        return 0
