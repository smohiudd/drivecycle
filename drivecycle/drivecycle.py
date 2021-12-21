import numpy as np
from drivecycle.trajectory import Trajectory
from drivecycle.plot import plot


class Drivecycle:
    def __init__(self):
        self.tvq = np.array([(0, 0, 0)])

    def drivecycle(self,
                   edges,
                   di=0,
                   vi=0,
                   ti=0,
                   a_max=1,
                   stops=None,
                   step=0.1,
                   stop_at_node=False,
                   kmh=True):

        stop = None
        conversion = 1000 / 3600

        for i in range(len(edges)):

            if kmh == True:
                conversion = 1000 / 3600
            else:
                conversion = 1

            try:
                v_target_next = edges[i + 1]["speed"] * conversion
            except:
                v_target_next = 0

            v_target = edges[i]["speed"] * conversion
            df = di + edges[i]["length"]

            if any(x in list(stops.keys())
                   for x in edges[i]["intersection"]) and stop_at_node == True:
                stop = np.random.randint(2)

            if stop:
                vf = 0
            else:
                if v_target_next >= v_target:
                    vf = v_target
                else:
                    vf = v_target_next

            traj = Trajectory(vi=vi,
                              v_target=v_target,
                              vf=vf,
                              di=di,
                              df=df,
                              ti=ti,
                              step=step)
            d = traj.const_accel(a_max=a_max).get_trajectory()

            # if len(d)==0:
            #     continue

            if stop:

                stop_max_time = stops[edges[i]["intersection"][0]]
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
