import geopandas as gpd
import numpy as np
import pandas as pd
from geopandas import GeoDataFrame


def cluster_nodes(df: GeoDataFrame, buffer: int = 50) -> GeoDataFrame:
    df["x"] = df["lr"]
    df["y"] = 0
    df = df.set_geometry(gpd.points_from_xy(df.x, df.y))

    merged = df["geometry"].buffer(buffer).unary_union
    node_clusters = gpd.GeoDataFrame(geometry=gpd.GeoSeries(merged.geoms))
    centroids = node_clusters.centroid
    node_clusters["x"] = centroids.x
    node_clusters["y"] = centroids.y

    df2 = gpd.sjoin(df, node_clusters, how="left", predicate="within")
    df2 = df2.rename(columns={"index_right": "cluster", "x_right": "x"})
    df2["x"] = df2["x"].round(2)

    agg_speed = pd.NamedAgg(column="speed", aggfunc=lambda x: np.mean(x))
    agg_ends = pd.NamedAgg(column="end", aggfunc=lambda x: x.to_list())

    result = df2.groupby("x").agg(speed=agg_speed, end=agg_ends).reset_index()
    result = result.rename(columns={"x": "lr"})

    return result[["speed", "end", "lr"]]
