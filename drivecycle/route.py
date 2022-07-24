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

    carryoverdistance = None

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
        if carryoverdistance:
            df = di + edges[i]["length"]+carryoverdistance
            carryoverdistance=None
        else:
            df = di + edges[i]["length"]

        if any(x in list(stops.keys())
               for x in edges[i]["intersection"]) and stop_at_node:
            stop = np.random.randint(2)

        if stop:
            vf = 0
            a = 1
        else:
            if v_target_next >= v_target:
                vf = v_target
            else:
                vf = v_target_next

        while True:
            try:
                d = trajectory.const_accel(vi=vi,
                                        v_target=v_target,
                                        vf=vf,
                                        di=di,
                                        df=df,
                                        ti=ti,
                                        step=step,
                                        a_max=a)
                break
            except AssertionError: # if the trajectory segment is not feasible then try the following:
                if v_target>=1.0 and vf>=1.0: # (1) reduce v_target and vf by 10% if they are not both less than 1 m/s
                    v_target = v_target*.9
                    vf = vf*.9
                    logging.info(f"Vi: {vi:.2f}. Reducing vf to {vf:.2f} and v_target to {v_target:.2f} at time {ti} and segment length {df-di}")
                else: 
                    if vi!=0.0: # (2) if that doesn't work then use a constant velocity accross the segment
                        tf = (df - di)/vi  # Constant veclocity using vi
                        d = np.array([[ti, vi, di], [ti+tf, vi, df]])
                        logging.info(
                            f'Could not complete segment: ti: {ti:.2f}, tf: {tf:.2f},  vi: {vi:.2f} , vf: {vf:.2f}, \
                                v_target:{v_target:.2f}, length: {edges[i]["length"]:.2f}')
                        break
                    else: # (3) if vi==0 then can't complete this segment. Carry over the distance for this segment to the next segment
                        d = np.array([[ti, vi, di]])
                        carryoverdistance = df-di
                        logging.info('Carry over segment length to next segment')
                        break


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
