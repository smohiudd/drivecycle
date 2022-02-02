import networkx as nx
from typing import List, Dict, Any, Tuple


class Graph:
    """Generate a path graph of a bus route

    Generate a path graph of a bus route using a list of dicts of edge
    attributed such as end node, speed, and linear reference. The purpose
    of this class is to simplify paths by clustering nearby intersections.

    Attributes:
        graph: Networkx graph of route
        source: First node of the graph
        target: Last node of the graph
        edges: List of Dict of edges

    """

    def __init__(self, edges: List[Dict[str, Any]]):

        self.graph = self.dict_to_graph(edges)
        self.source = 0
        self.target = len(edges)
        self.edges = edges

    def get_source_target(self) -> Tuple[int, int]:
        return (self.source, self.target)

    @staticmethod
    def dict_to_graph(data_: List[Dict[str, Any]]) -> nx.Graph:

        G = nx.path_graph(len(data_) + 1, nx.DiGraph())
        keys = list(data_[0].keys())

        x = 0
        intersection = [None]

        for i, (u, v) in enumerate(G.edges):
            for key in keys:
                G[u][v][key] = data_[i][key]

            G.nodes[u]["intersection"] = intersection
            G.nodes[u]["LR"] = x

            G.nodes[v]["intersection"] = data_[i]["intersection"]
            G.nodes[v]["LR"] = x + data_[i]["length"]

            x = G.nodes[v]["LR"]
            intersection = G.nodes[v]["intersection"]

        return G

    def get_edges(self) -> List[Dict[str, Any]]:
        """Get list of edges from networkx DiGraph.

        Returns:
            list: List of dictionaries of route path edges.

        """
        edges = []

        for u, v in nx.bfs_edges(self.graph, self.source):
            edges.append(self.graph[u][v])

        return edges

    def consolidate_intersections(
        self,
        filters: List[str] = ["tertiary", "secondary",
                              "bus_stop"]) -> nx.Graph:
        """Consolidate intersections that are clustered together

        Args:
            filters (list): list intersections to be clustered.
        Returns:
            Networkx DiGraph
        """

        H = self.graph.copy()

        for u, v in nx.bfs_successors(self.graph, 0):

            n = v[0]

            in_edge = list(H.in_edges(n))
            out_edge = list(H.out_edges(n))

            if len(in_edge) > 0 and len(out_edge) > 0:

                u = in_edge[0]
                v = out_edge[0]

                e1 = H.edges[u]
                e2 = H.edges[v]

                l1 = e1["length"]
                l2 = e2["length"]

                if l1 < 100 and any(x in H.nodes[n]["intersection"]
                                    for x in filters) and any(
                                        x in H.nodes[u[0]]["intersection"]
                                        for x in filters):
                    # print(H.nodes[u[0]]["intersection"],H.nodes[n]["intersection"])
                    H.add_edge(u[0],
                               v[1],
                               way_id=e1["way_id"] + e2["way_id"],
                               speed=e1["speed"],
                               length=l1 + l2,
                               intersection=H.nodes[v[1]]["intersection"])
                    H.nodes[u[0]]["intersection"] = H.nodes[n][
                        "intersection"] + H.nodes[u[0]]["intersection"]
                    H.remove_node(n)

                elif l2 < 100 and any(x in H.nodes[n]["intersection"]
                                      for x in filters) and any(
                                          x in H.nodes[v[1]]["intersection"]
                                          for x in filters):
                    # print(H.nodes[v[1]]["intersection"],H.nodes[n]["intersection"])
                    H.add_edge(u[0],
                               v[1],
                               way_id=e1["way_id"] + e2["way_id"],
                               speed=e1["speed"],
                               length=l1 + l2,
                               intersection=H.nodes[v[1]]["intersection"] +
                               H.nodes[n]["intersection"])
                    H.nodes[v[1]]["intersection"] = H.nodes[n][
                        "intersection"] + H.nodes[v[1]]["intersection"]
                    H.remove_node(n)

                else:
                    continue

        self.graph = H
        return H

    def simplify_graph(
        self,
        filters: List[str] = ["tertiary", "secondary", "bus_stop"]
    ) -> 'nx.Graph[Any]':
        """Method to simplify graph by clustering adjacent nodes

        This method clusters adjacent nodes that are included in the filters list
        and that have adjacent edges that have the same speed.

        Args:
            filters (list): list of intersections that should NOT be merged
        Returns:
            Networkx DiGraph
        """

        H = self.graph.copy()

        for u, v in nx.bfs_successors(self.graph, 0):

            n = v[0]

            in_edge = list(H.in_edges(n))
            out_edge = list(H.out_edges(n))

            if len(in_edge) > 0 and len(out_edge) > 0:

                u = in_edge[0]
                v = out_edge[0]

                e1 = H.edges[u]
                e2 = H.edges[v]

                if e1["speed"] == e2["speed"] and \
                    not any(x in e1["intersection"] for x in filters):

                    sum_length = e1["length"] + e2["length"]
                    speed = e1["speed"]
                    way_ids = e1["way_id"] + e2["way_id"]
                    intersections = e1["intersection"] + e2["intersection"]

                    H.add_edge(u[0],
                               v[1],
                               way_id=way_ids,
                               speed=speed,
                               length=sum_length,
                               intersection=intersections)
                    H.remove_node(n)

        self.graph = H
        return H

    def include_stops(self, stops: List[float]) -> 'nx.Graph[Any]':
        """Method to insert bus stop location in networkx DiGraph

        Args:
            stops (list): List of linear referenced location of bus stops
        Returns:
            Networkx DiGraph

        """
        J = self.graph.copy()

        for u, v in nx.bfs_edges(self.graph, 0):
            di = self.graph.nodes[u]["LR"]
            df = self.graph.nodes[v]["LR"]

            bus_stops = [i for i in stops if i >= di and i < df]

            if len(bus_stops) > 0:

                for stop in bus_stops:
                    J.add_node(stop, intersection=["bus_stop"], LR=stop)

                stops1 = [u, *bus_stops, v]

                for i in range(len(stops1) - 1):
                    J.add_edge(stops1[i],
                               stops1[i + 1],
                               way_id=self.graph[u][v]["way_id"],
                               speed=self.graph[u][v]["speed"],
                               length=J.nodes[stops1[i + 1]]["LR"] -
                               J.nodes[stops1[i]]["LR"],
                               intersection=J.nodes[stops1[i +
                                                           1]]["intersection"])
                J.remove_edge(u, v)

        self.graph = J
        return J
