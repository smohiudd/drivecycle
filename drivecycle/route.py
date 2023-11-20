import math
from typing import Any, Dict, Union

import numpy as np
from geopandas import GeoDataFrame
from pandas import DataFrame

from drivecycle import trajectory


def _should_stop(x: Any, stop_params: Dict[str, int]) -> int:
    if isinstance(x, list):
        if any(i in x for i in list(stop_params.keys())):
            return np.random.randint(2)
        else:
            return 0


def _get_vf(x: Any) -> float:
    if x["stop"]:
        return 0
    else:
        if x["v_target_next"] >= x["v_target"]:
            return x["v_target"] # end speed should not be higher than current segment speed
        else:
            return x["v_target_next"]


def _get_trajectory(x: Any, step: float = 1.0, a_max: float = 2.0):
    """
    "x","x_","d", "vi","v_target","v_target_next","vf","stop"
    """
    # vf and v_target adjustment needed if the trajectory is not feasible
    # this may result in a no stop condition
    if np.abs(np.square(x[6]) - np.square(x[3])) / 2 > a_max * x[2]:
        vf = np.sqrt(2 * a_max * x[2] + np.square(x[3])) * 0.95
        v_target = vf
    else:  # else go with values from the table
        vf = x[6]
        v_target = x[4]

    traj = trajectory.const_accel(
        vi=x[3],
        v_target=v_target,
        vf=vf,
        di=x[1],
        df=x[2] + x[1],
        ti=0,
        step=step,
        a_max=a_max,
    )

    if vf == 0: #pad the trajectory with zeros for the stop duration
        stop_time = np.random.randint(30, 120)
        pad = math.floor(stop_time / step)
        vel = np.pad(traj[:, 1], (0, pad), "constant")
        dist = np.pad(traj[:, 2], (0, pad), "edge")
        return np.stack((vel, dist), axis=-1)
    else:
        return traj[:, 1:3]


def _df_transformation(
    df: Union[GeoDataFrame, DataFrame], stop_params: Dict[str, int]
) -> np.ndarray:
    df = df.rename(columns={"speed": "v_target", "lr": "x"})

    # find out the speed of the next segment
    df["v_target_next"] = df["v_target"].shift(-1)

    # do we stop at the next end of the current segment
    df["stop"] = df["end"].apply(lambda x: _should_stop(x, stop_params))

    # di and df calculation
    df["x_"] = df["x"].shift(1, fill_value=0)
    df["d"] = df.apply(lambda x: (x["x_"] - x["x"]) * -1, axis=1)

    # get final speed of current segment based on if stop or speed of next segment
    df["vf"] = df.apply(_get_vf, axis=1)
    df.loc[len(df.index) - 1, "vf"] = 0 #final segment should have 0 speed

    # initial speed of current segment
    df["vi"] = df["vf"].shift(1, fill_value=0)

    output = df[
        ["x", "x_", "d", "vi", "v_target", "v_target_next", "vf", "stop"]
    ].to_numpy()

    return output


def sequential(
    df: DataFrame,
    stops: Dict[str, int],
    a_max: float = 2,
    step: float = 1,
) -> np.ndarray:
    output = _df_transformation(df, stops)

    v = []
    for i in range(output.shape[0]):
        v.append(np.apply_along_axis(_get_trajectory, 0, output[i], step, a_max))

    v_ = np.concatenate(v) #combine all the segments 
    t = np.arange(0, v_.shape[0], 1, dtype=int).reshape(v_.shape[0], 1) #add time column to array
    tvq = np.hstack((t, v_))

    return tvq
