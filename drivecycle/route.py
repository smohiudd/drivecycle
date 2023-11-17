import numpy as np
from drivecycle import trajectory
from geopandas import GeoDataFrame
from pandas import DataFrame
from typing import Union
import math

from typing import List, Dict, Any
# import numpy.typing as npt

def _should_stop(
    x: Any, 
    stop_params: Dict[str, int])->int:

    if isinstance(x, list):
        if any(i in x for i in list(stop_params.keys())):
            return np.random.randint(2)
        else:
            return 0

def _get_vf(x: Any)->float:
    if x["stop"]:
        return 0
    else:
        if x["v_target_next"] >= x["v_target"]:
            return x["v_target"]
        else:
            return x["v_target_next"]

def _get_trajectory(
    x: Any,
    step: float=1.0, 
    a_max: float=2.0):
    """
    "x","x_","d", "vi","v_target","v_target_next","vf","stop"
    """
    stop_time=np.random.randint(30,120)
    pad = math.floor(stop_time/step)
    try:
        traj = trajectory.const_accel(vi=x[3],
                            v_target=x[4],
                            vf=x[6],
                            di=x[1],
                            df=x[2]+x[1],
                            ti=0,
                            step=step,
                            a_max=a_max)
        
        if x[7]:
            vel = np.pad(traj[:,1], (0, pad), 'constant')
            dist = np.pad(traj[:,2], (0, pad), 'edge')
            return np.stack((vel,dist),axis=-1)
        else:
            return traj[:,1:3]
    except Exception as e:
        print(x[0], e)
        return [0]

def _df_transformation(
    df: Union[GeoDataFrame, DataFrame],
    stop_params: Dict[str, int]
    )-> np.ndarray:

    df = df.rename(columns={"speed": "v_target", "lr":"x"})

    df["v_target_next"]=df["v_target"].shift(-1)

    df["stop"] = df["end"].apply(lambda x: _should_stop(x,stop_params))

    df["vf"] = df.apply(_get_vf, axis=1)
    df.loc[len(df.index)-1, 'vf'] = 0

    df["x_"] = df["x"].shift(1,fill_value=0)
    df["d"] = df.apply(lambda x: (x["x_"]-x["x"])*-1, axis=1)

    df["vi"] = df["vf"].shift(1,fill_value=0)

    output= df[["x","x_","d", "vi","v_target","v_target_next","vf","stop"]].to_numpy()
    
    return output

def sequential(
    df: DataFrame,
    stops: Dict[str, int],
    a_max: float = 1,
    step: float = 0.1,
    ) -> np.ndarray:

    output = _df_transformation(df, stops)

    v = []
    for i in range(output.shape[0]):
        v.append(np.apply_along_axis(_get_trajectory, 0, output[i],step, a_max))

    v_= np.concatenate(v)
    t = np.arange(0, v_.shape[0], 1, dtype=int).reshape(v_.shape[0],1)
    tvq = np.hstack((t, v_))

    return tvq