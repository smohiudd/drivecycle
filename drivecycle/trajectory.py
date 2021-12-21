import math
import matplotlib.pyplot as plt
# from typing import Any, Dict, Iterable, List, Optional, Union
from drivecycle.plot import plot


class Trajectory:
    def __init__(self, vi=0, v_target=13, vf=0, di=0, df=100, ti=0, step=0.1):
        self.vi = vi
        self.v_target = v_target
        self.vf = vf
        self.di = di
        self.df = df
        self.ti = ti
        self.step = step
        self.tvq = []

    def const_accel(self, a_max=1):

        t = self.ti

        if (self.df - self.di) * a_max > (pow(self.v_target, 2) - (
            (pow(self.vi, 2) + pow(self.vf, 2)) / 2)):

            Ta = (self.v_target - self.vi) / a_max
            Td = (self.v_target - self.vf) / a_max
            T = self.ti+((self.df-self.di)/self.v_target)+((self.v_target/(2*a_max))*pow((1-(self.vi/self.v_target)),2)) \
                + ((self.v_target/(2*a_max))*pow((1-(self.vf/self.v_target)),2))

            while t <= T:
                if t >= self.ti and t < self.ti + Ta and Ta != 0:
                    v = self.vi + (
                        (self.v_target - self.vi) / Ta) * (t - self.ti)
                    q = self.di + (self.vi * (t - self.ti)) + ((
                        (self.v_target - self.vi) / (2 * Ta)) * pow(
                            (t - self.ti), 2))
                elif t >= self.ti + Ta and t < T - Td:
                    v = self.v_target
                    q = self.di + (self.vi * (Ta / 2)) + (self.v_target *
                                                          (t - self.ti -
                                                           (Ta / 2)))
                elif t >= T - Td and t <= T:
                    v = self.vf + ((self.v_target - self.vf) / Td) * (T - t)
                    q = self.df - (self.vf *
                                   (T - t)) - (((self.v_target - self.vf) /
                                                (2 * Td)) * pow((T - t), 2))
                elif Ta == 0:
                    v = self.v_target
                    q = self.di + (self.v_target * t)
                else:
                    v = None
                    q = None

                if v < 0.1:
                    v = 0
                self.tvq.append((t, v, q))
                t += self.step

        else:
            vlim = math.sqrt(((self.df - self.di) * a_max) +
                             ((pow(self.vi, 2) + pow(self.vf, 2)) / 2))
            Ta = (vlim - self.vi) / a_max
            Td = (vlim - self.vf) / a_max
            T = self.ti + Ta + Td

            while t <= T:
                if t >= self.ti and t < self.ti + Ta:
                    v = self.vi + ((vlim - self.vi) / Ta) * (t - self.ti)
                    q = self.di + (self.vi *
                                   (t - self.ti)) + (((vlim - self.vi) /
                                                      (2 * Ta)) * pow(
                                                          (t - self.ti), 2))
                elif t >= self.ti + Ta and t <= T and Td != 0:
                    v = self.vf + ((vlim - self.vf) / Td) * (T - t)
                    q = self.df - (self.vf * (T - t)) - (((vlim - self.vf) /
                                                          (2 * Td)) * pow(
                                                              (T - t), 2))
                elif Td == 0:
                    v = self.vf
                    q = self.di + (self.df * t)
                else:
                    v = None
                    q = None

                if v < 0.1:
                    v = 0
                self.tvq.append((t, v, q))
                t += self.step

        return self

    def get_trajectory(self):

        assert len(self.tvq) > 0, "No trajectory values."
        return self.tvq

    def plot_vt(self):
        t = [i[0] for i in self.tvq]
        v = [i[1] for i in self.tvq]

        plot(v, t)

    def plot_vd(self):
        d = [i[2] for i in self.tvq]
        v = [i[1] for i in self.tvq]

        plot(v, d)
