import math
import numpy as np
import numpy.typing as npt
from typing import Any


def const_accel(vi: float = 0.0,
                v_target: float = 13.0,
                vf: float = 0.0,
                di: float = 0.0,
                df: float = 100.0,
                ti: float = 0.0,
                step: float = 0.1,
                a_max: float = 1.0) -> npt.NDArray[Any]:
    """Generate trajectory using constant acceleration.

    Generate linear trajectory with parabolic bends (trapezoidal).
    The trajectory is divided into three parts: the acceleration phase,
    constant velocity and deceleration phase. In some cases, the constant
    velocity phase will not be reached in which case we only have
    a acceleration and deceleration phase.

    Biagiotti, L., Melchiorri, C. (2008). Trajectory Planning for Automatic Machines
    and Robots. Springer-Verlag.

    Args:
        vi (float): initial velocity 
        v_target (float): target velocity 
        vf (float): final velocity 
        di (float): initial position 
        df (float): final position 
        ti (float): initial time
        step (float): time step
        a_max (float): maximum acceleration
    Returns:
        list: (n,3) numpy array of time, velocity, distance of trajectory

    """

    tvq = np.array([(ti, vi, di)])

    t = ti + step

    # We need to first check if the trajectory is even possible given
    # the accel, vi, vf and distance

    assert np.abs(pow(vf, 2) - pow(vi, 2)) / 2 < a_max * (
        df - di), "Error 1: Trajectory is not possible given inputs."
    assert np.sqrt(
        (df - di) / a_max
    ) * 2 > 1, "Error 2: Trapezoidal trajectory is not possible given inputs."

    
    # If the below condition is true, then the target velocity is met 

    if (df - di) * a_max > (pow(v_target, 2) -
                            ((pow(vi, 2) + pow(vf, 2)) / 2)):

        Ta = np.abs(v_target -
                    vi) / a_max  # Use abs if vi is greater than v_target
        Td = (v_target - vf) / a_max
        T = ti + ((df - di) / v_target) \
            + ((v_target / (2 * a_max)) * pow((1 - (vi / v_target)), 2)) \
            + ((v_target / (2 * a_max)) * pow((1 - (vf / v_target)), 2))

        # print('Case 1')
        # print(f"Ta: {Ta}, Td: {Td}, T: {T}")

        while t <= T:
            if t >= ti and t < ti + Ta and Ta != 0:  # Acceleration phase
                v = _accel_v(vi, v_target, Ta, t, ti)
                q = _accel_q(di, vi, ti, v_target, Ta, t)
            elif t >= ti + Ta and t < T - Td:  # Constant velocity phase
                v = v_target
                q = _const_q(di, vi, Ta, v_target, ti, t)
            elif t >= T - Td and t <= T and Td != 0:  # Deceleration phase
                v = _decel_v(vf, v_target, Td, T, t)
                q = _decel_q(df, vf, T, t, v_target, Td)
            elif Ta == 0:  # case when Vi and v_target are equal
                v = v_target
                q = di + (v_target * t)
            else:
                raise ValueError(
                    'Cannot create trajectory using input values.')

            s = np.column_stack((t, v, q))
            tvq = np.concatenate([tvq, s])
            t += step

    else:
        vlim = math.sqrt(((df - di) * a_max) + ((pow(vi, 2) + pow(vf, 2)) / 2))
        Ta = (vlim - vi) / a_max
        Td = (vlim - vf) / a_max
        T = ti + Ta + Td

        # print('Case 2')
        # print(f"Ta: {Ta}, Td: {Td}, T: {T}, vlim: {vlim}")

        while t <= T:
            if t >= ti and t < ti + Ta:
                v = _accel_v(vi, vlim, Ta, t, ti)
                q = _accel_q(di, vi, ti, vlim, Ta, t)
            elif t >= ti + Ta and t <= T and Td != 0:
                v = _decel_v(vf, vlim, Td, T, t)
                q = _decel_q(df, vf, T, t, vlim, Td)
            elif Td == 0:
                v = vf
                q = di + (df * t)
            else:
                raise ValueError(
                    'Cannot create trajectory using input values.')

            s = np.column_stack((t, v, q))
            tvq = np.concatenate([tvq, s])
            t += step

    return tvq 
    
    # TODO: need a different data structure for the time, velocit, data return. 
    # Maybe a dictionary


def _accel_q(di: float, vi: float, ti: float, v_target: float, Ta: float,
             t: float) -> float:
    return di + (vi * (t - ti)) + (((v_target - vi) / (2 * Ta)) * pow(
        (t - ti), 2))


def _accel_v(vi: float, v_target: float, Ta: float, t: float,
             ti: float) -> float:
    return vi + ((v_target - vi) / Ta) * (t - ti)


def _const_q(di: float, vi: float, Ta: float, v_target: float, ti: float,
             t: float) -> float:
    return di + (vi * (Ta / 2)) + (v_target * (t - ti - (Ta / 2)))


def _decel_q(df: float, vf: float, T: float, t: float, v_target: float,
             Td: float) -> float:
    return df - (vf * (T - t)) - (((v_target - vf) / (2 * Td)) * pow(
        (T - t), 2))


def _decel_v(vf: float, v_target: float, Td: float, T: float,
             t: float) -> float:
    return vf + ((v_target - vf) / Td) * (T - t)
