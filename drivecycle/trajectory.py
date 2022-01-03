import math
import numpy as np
from typing import Any


class Trajectory:

    def __init__(self,
                 vi: float = 0.0,
                 v_target: float = 13.0,
                 vf: float = 0.0,
                 di: float = 0.0,
                 df: float = 100.0,
                 ti: float = 0.0,
                 step: float = 0.1):
        self.vi = vi
        self.v_target = v_target
        self.vf = vf
        self.di = di
        self.df = df
        self.ti = ti
        self.step = step
        self.tvq = np.array([(ti, vi, di)])

    def const_accel(self, a_max: float = 1.0) -> 'Trajectory':

        t = self.ti

        assert np.abs(pow(self.vf, 2) - pow(self.vi, 2)) / 2 < a_max * (
            self.df - self.di), "Trajectory is not possible given inputs."
        assert np.sqrt(
            (self.df - self.di) / a_max
        ) * 2 > 1, "Trapezoidal trajectory is not possible given inputs."

        if (self.df - self.di) * a_max > (pow(self.v_target, 2) - (
            (pow(self.vi, 2) + pow(self.vf, 2)) / 2)):

            Ta = np.abs(self.v_target - self.vi
                        ) / a_max  # Use abs if vi is greater than v_target
            Td = (self.v_target - self.vf) / a_max
            T = self.ti + ((self.df - self.di) / self.v_target) \
                + ((self.v_target / (2 * a_max)) * pow((1 - (self.vi / self.v_target)), 2)) \
                + ((self.v_target / (2 * a_max)) * pow((1 - (self.vf / self.v_target)), 2))

            # print('Case 1')
            # print(f"Ta: {Ta}, Td: {Td}, T: {T}")

            while t <= T:
                if t >= self.ti and t < self.ti + Ta and Ta != 0:  # Acceleration phase
                    v = accel_v(self.vi, self.v_target, Ta, t, self.ti)
                    q = accel_q(self.di, self.vi, self.ti, self.v_target, Ta,
                                t)
                elif t >= self.ti + Ta and t < T - Td:  # Constant velocity phase
                    v = self.v_target
                    q = const_q(self.di, self.vi, Ta, self.v_target, self.ti,
                                t)
                elif t >= T - Td and t <= T:  # Deceleration phase
                    v = decel_v(self.vf, self.v_target, Td, T, t)
                    q = decel_q(self.df, self.vf, T, t, self.v_target, Td)
                elif Ta == 0:  # case when Vi and v_target are equal
                    v = self.v_target
                    q = self.di + (self.v_target * t)
                else:
                    raise ValueError(
                        'Cannot create trajectory using input values.')

                s = np.column_stack((t, v, q))
                self.tvq = np.concatenate([self.tvq, s])
                t += self.step

        else:
            vlim = math.sqrt(((self.df - self.di) * a_max) +
                             ((pow(self.vi, 2) + pow(self.vf, 2)) / 2))
            Ta = (vlim - self.vi) / a_max
            Td = (vlim - self.vf) / a_max
            T = self.ti + Ta + Td

            # print('Case 2')
            # print(f"Ta: {Ta}, Td: {Td}, T: {T}, vlim: {vlim}")

            while t <= T:
                if t >= self.ti and t < self.ti + Ta:
                    v = accel_v(self.vi, vlim, Ta, t, self.ti)
                    q = accel_q(self.di, self.vi, self.ti, vlim, Ta, t)
                elif t >= self.ti + Ta and t <= T and Td != 0:
                    v = decel_v(self.vf, vlim, Td, T, t)
                    q = decel_q(self.df, self.vf, T, t, vlim, Td)
                elif Td == 0:
                    v = self.vf
                    q = self.di + (self.df * t)
                else:
                    raise ValueError(
                        'Cannot create trajectory using input values.')

                s = np.column_stack((t, v, q))
                self.tvq = np.concatenate([self.tvq, s])
                t += self.step

        return self

    def get_trajectory(self) -> 'np.ndarray[Any,Any]':

        assert len(self.tvq) > 0, "No trajectory values."
        return self.tvq


def accel_q(di: float, vi: float, ti: float, v_target: float, Ta: float,
            t: float) -> float:
    return di + (vi * (t - ti)) + (((v_target - vi) / (2 * Ta)) * pow(
        (t - ti), 2))


def accel_v(vi: float, v_target: float, Ta: float, t: float,
            ti: float) -> float:
    return vi + ((v_target - vi) / Ta) * (t - ti)


def const_q(di: float, vi: float, Ta: float, v_target: float, ti: float,
            t: float) -> float:
    return di + (vi * (Ta / 2)) + (v_target * (t - ti - (Ta / 2)))


def decel_q(df: float, vf: float, T: float, t: float, v_target: float,
            Td: float) -> float:
    return df - (vf * (T - t)) - (((v_target - vf) / (2 * Td)) * pow(
        (T - t), 2))


def decel_v(vf: float, v_target: float, Td: float, T: float,
            t: float) -> float:
    return vf + ((v_target - vf) / Td) * (T - t)
