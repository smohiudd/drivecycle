import numpy as np
from drivecycle import trajectory

from typing import List, Dict, Any
# import numpy.typing as npt

import logging

logging.getLogger().setLevel(logging.INFO)


def sequential(edges: List[Dict[str, Any]],
               stops: Dict[str, int],
               di: float = 0,
               vi: float = 0,
               ti: float = 0,
               a_max: float = 1,
               step: float = 0.1,
               stop_at_node: bool = False,
               kmh: bool = True) -> 'np.ndarray':  # type: ignore
    """Generate route drivecycle.

    Generate a drivecycle which is formed from a collection or 
    sequence of trajectories. 

    Args:
        edges (list): list of dictionary of route edges
        stops (dict): dict of stops categories and stop durations
        di (float): initial position
        vi (float): initial velocity
        ti (float): initial time
        a_max (float): maximum acceleration
        step (float): time step
        kmh (bool): kilometers per hour

    Returns:
        list: (n,3) numpy array of time, velocity, distance of drivecycle

    """

    tvq = np.array([(ti, vi, di)])

    stop = None
    conversion = 1000 / 3600

    keys = list(stops.keys())

    a = a_max

    for i in range(len(edges)):

        if kmh:
            conversion = 1000 / 3600
        else:
            conversion = 1

        try:
            v_target_next = edges[i + 1]["speed"] * conversion
        except IndexError:
            v_target_next = 0

        v_target = edges[i]["speed"] * conversion
        df = di + edges[i]["length"]

        if any(x in list(stops.keys())
               for x in edges[i]["intersection"]) and stop_at_node:
            stop = np.random.randint(2)

        if stop:
            vf = 0
            a = 2
        else:
            if v_target_next >= v_target:
                vf = v_target
            else:
                vf = v_target_next

        try:
            d = trajectory.const_accel(vi=vi,
                                       v_target=v_target,
                                       vf=vf,
                                       di=di,
                                       df=df,
                                       ti=ti,
                                       step=step,
                                       a_max=a)
        except AssertionError: # if the trajectory is not feasible then use a constant velocity
            tf = (df - di) * vi  # Constant veclocity using initial
            d = np.array([[ti, vi, di], [tf, vi, df]])
            logging.info(
                f'Could not complete segment: vi: {vi:.2f} , vf: {vf:.2f}, \
                    v_target:{v_target:.2f}, length: {edges[i]["length"]:.2f}')

        if stop:

            stop_id = next(x for x in keys if x in edges[i]["intersection"])
            stop_max_time = stops[stop_id]
            stop_time = np.random.randint(5, stop_max_time)

            t = np.linspace(d[-1][0] + step, d[-1][0] + stop_time, 5)
            v = np.zeros(5)
            q = np.repeat(d[-1][2], 5)
            s = np.column_stack((t, v, q))
            d = np.concatenate([d, s])

        di = d[-1][2]
        ti = d[-1][0]
        vi = d[-1][1]

        tvq = np.concatenate([tvq, d[:-1]])

        stop = 0

    return tvq[1:]  # type: ignore
