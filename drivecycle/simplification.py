import geopandas as gpd
import pandas as pd
from geopandas import GeoDataFrame
from pandas import DataFrame
from typing import Union, List
import numpy as np


# def create_df(trace):
#     df = gpd.GeoDataFrame(trace.json()["edges"])
#     df["end"] = df["end_node"].map(lambda x: x["intersecting_edges"][0]["road_class"] if "intersecting_edges" in x else None) 
#     df["lr"]=df["length"].cumsum()*1000
#     df["speed"]=df.apply(lambda x: x["speed"]*(1000/3600), axis=1)
#     return df[["speed","end","lr"]]

# def include_stops(
#         df: Union[GeoDataFrame, Dataframe],
#         stops: List[float], 
#         tag: str
#     ) -> Union[GeoDataFrame, Dataframe]:

#     df1 = pd.DataFrame({
#         "speed": np.NaN,
#         "end": tag,
#         "lr": stops
#     })
    
#     resulst = pd.concat(
#         [df,df1],axis=0
#         ).reset_index()[["speed","end","lr"]]
#         .sort_values("lr")
#         .ffill()
#         .fillna(0)

#     return result

def cluster_nodes(
        df: GeoDataFrame, 
        buffer: int=50
    )-> GeoDataFrame:

    df["x"]=df["lr"]
    df["y"]=0
    df = df.set_geometry(gpd.points_from_xy(df.x, df.y))

    merged = df["geometry"].buffer(buffer).unary_union
    node_clusters = gpd.GeoDataFrame(geometry=gpd.GeoSeries(merged.geoms))
    centroids = node_clusters.centroid
    node_clusters["x"] = centroids.x
    node_clusters["y"] = centroids.y

    df2 = gpd.sjoin(df, node_clusters, how="left", predicate="within")
    df2 = df2.rename(columns={"index_right": "cluster", "x_right":"x"})
    df2["x"]= df2["x"].round(2)

    agg_speed = pd.NamedAgg(column="speed", aggfunc=lambda x: np.mean(x))
    agg_ends = pd.NamedAgg(column="end", aggfunc=lambda x: x.to_list())

    result = df2.groupby("x").agg(speed=agg_speed, end=agg_ends).reset_index()
    result = result.rename(columns={"x": "lr"})

    return result[["speed","end","lr"]]

