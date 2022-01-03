import numpy as np
from drivecycle import trajectory

from typing import List, Dict, Any


class Drivecycle:

    def __init__(self,
                 edges: List[Dict[str, Any]],
                 stops: Dict[str, int],
                 di: float = 0,
                 vi: float = 0,
                 ti: float = 0,
                 a_max: float = 1,
                 step: float = 0.1,
                 stop_at_node: bool = False,
                 kmh: bool = True):

        self.tvq = np.array([(0, 0, 0)])
        self.edges = edges
        self.di = di
        self.vi = vi
        self.ti = ti
        self.a_max = a_max
        self.stops = stops
        self.step = step
        self.stop_at_node = stop_at_node
        self.kmh = kmh

    def get_trajectory(self) -> 'np.ndarray[Any,Any]':

        stop = None
        conversion = 1000 / 3600
        di = self.di
        ti = self.ti
        vi = self.vi

        for i in range(len(self.edges)):

            if self.kmh:
                conversion = 1000 / 3600
            else:
                conversion = 1

            try:
                v_target_next = self.edges[i + 1]["speed"] * conversion
            except:
                v_target_next = 0

            v_target = self.edges[i]["speed"] * conversion
            df = di + self.edges[i]["length"]

            if any(x in list(self.stops.keys()) for x in self.edges[i]
                   ["intersection"]) and self.stop_at_node:
                stop = np.random.randint(2)

            if stop:
                vf = 0
            else:
                if v_target_next >= v_target:
                    vf = v_target
                else:
                    vf = v_target_next

            traj = trajectory.Trajectory(vi=vi,
                                         v_target=v_target,
                                         vf=vf,
                                         di=di,
                                         df=df,
                                         ti=ti,
                                         step=self.step)
            d = traj.const_accel(a_max=self.a_max).get_trajectory()

            # if len(d)==0:
            #     continue

            if stop:

                stop_max_time = self.stops[self.edges[i]["intersection"][0]]
                stop_time = np.random.randint(5, stop_max_time)

                x = np.linspace(d[-1][0], d[-1][0] + stop_time, 5)
                v = np.zeros(5)
                q = np.repeat(d[-1][2], 5)
                s = np.column_stack((x, v, q))
                d = np.concatenate([d, s])

            self.tvq = np.concatenate([self.tvq, d])

            di = self.tvq[-1][2]
            ti = d[-1][0]
            vi = d[-1][1]
            stop = 0

            del traj

        return self.tvq
