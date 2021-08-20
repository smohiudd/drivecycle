import networkx as nx

class Graph:

    """Utility class to recreate graph vehicle path

    Args:
         edges: list of dictionaries with with way_id, speed, length and intersection keys
    Returns:
         Networkx Graph class
    """

    def __init__(self,edges):

        G = nx.path_graph(len(edges)+1)
        i=0
        x=0
        for u, v in G.edges:
            if u==0:
                G[u][v]['way_id']=[edges[i]["way_id"]]
                G[u][v]['speed']=edges[i]["speed"]
                G[u][v]['length']=edges[i]["length"]
                G[u][v]["intersection"]=edges[i]["intersection"]

                G.nodes[v]["intersection"]=edges[i]["intersection"]
                G.nodes[v]["LR"]=x+edges[i]["length"]
                G.nodes[u]["intersection"]=[None]
                G.nodes[u]["LR"]=0
            else:
                G[u][v]['way_id']=[edges[i]["way_id"]]
                G[u][v]['speed']=edges[i]["speed"]
                G[u][v]['length']=edges[i]["length"]
                G[u][v]["intersection"]=edges[i]["intersection"]

                G.nodes[v]["intersection"]=edges[i]["intersection"]
                G.nodes[v]["LR"]=x+edges[i]["length"]

            i+=1
            x=G.nodes[v]["LR"]
        
        self.init_graph = G
        self.source = 0
        self.target = len(edges)
        self.edges = edges
    
    def get_source_target(self,):
        return (self.source,self.target)

    def simplify_graph(self,filters=["tertiary","secondary"]):

        """Utility function to simplify graph by mergeing adjacent edges with the same speed

        Args:
            filers: list of intersections that should NOT be merged
        Returns:
            Networkx Graph class
        """

        H = self.init_graph.copy()

        for u,v,d in self.init_graph.edges.data():
            n = list(H.neighbors(u))

            if len(n)==2:
                e1 = H[u][n[0]]
                e2 = H[u][n[1]]
                
                if  e1["intersection"]==e2["intersection"] and \
                    any(x in e1["intersection"] for x in filters) and \
                    e1["speed"]==e2["speed"] and \
                    (e1["length"] < 10 or e2["length"] < 10):
                    
                    sum_length = e1["length"] + e2["length"]
                    speed = e1["speed"]
                    way_ids = e1["way_id"]+e2["way_id"]
                    
                    H.add_edge(n[0],n[1],way_id = way_ids,speed=speed,length=sum_length,intersection=e1["intersection"])
                    H.remove_node(u)

                elif e1["speed"]==e2["speed"] and \
                    (not any(x in e1["intersection"] for x in filters) and "intersection" in e1) and \
                    (not any(x in e2["intersection"] for x in filters) and "intersection" in e2):
                    
                    sum_length = e1["length"] + e2["length"]
                    speed = e1["speed"]
                    way_ids = e1["way_id"]+e2["way_id"]
                    intersections = e1["intersection"]+e2["intersection"]
                    
                    H.add_edge(n[0],n[1],way_id = way_ids,speed=speed,length=sum_length,intersection=intersections)
                    H.remove_node(u)
                
                else:
                    continue

        return H

def include_stops(H,stops=[]):

    """Utility function to insert bus stop location in graph

    Args:
         H: Networkx Graph object
         stops: List of linear referenced location of bus stops
    Returns:
         Networkx Graph class

    """
    J = H.copy()

    for u,v,d in H.edges.data():
        di = J.nodes[u]["LR"]
        df = J.nodes[v]["LR"]
        
        bus_stops = ["st-"+str(i) for i in stops if i>=di and i<df]

        if len(bus_stops)>0:

            for stop in bus_stops:
                J.add_node(stop,intersection="bus_stop",LR=float(stop.split('-')[1]))

            stops1 = [u,*bus_stops,v]
            nx.add_path(J,stops1,way_id=J[u][v]["way_id"], speed=J[u][v]["speed"],length="",intersection="")
            J.remove_edge(u,v)

            for stop in bus_stops:
                n = list(J.neighbors(stop))

                J[n[0]][stop]["length"]=J.nodes[stop]["LR"]-J.nodes[n[0]]["LR"]
                J[n[0]][stop]["intersection"]=["bus_stop"]        

                if n[1]==v and len(n)>0:
                    J[stop][n[1]]["length"]=J.nodes[n[1]]["LR"]-J.nodes[stop]["LR"]
                    J[stop][n[1]]["intersection"]=J.nodes[n[1]]["intersection"]
                else:
                    J[stop][n[1]]["length"]=J.nodes[n[1]]["LR"]-J.nodes[stop]["LR"]
                    J[stop][n[1]]["intersection"]=["bus_stop"]
                
    
    return J

def get_edges(G,nodes):

    """Utility function to get list of edges in the following format:

    [{'way_id': [1, 2], 'speed': 20, 'length': 100, 'intersection': ['bus_stop']},
    {'way_id': [1, 2], 'speed': 20, 'length': 145, 'intersection': ['primary']},
    {'way_id': [3], 'speed': 50, 'length': 122, 'intersection': ['bus_stop']},
    {'way_id': [3], 'speed': 50, 'length': 28, 'intersection': ['primary']},
    {'way_id': [4], 'speed': 50, 'length': 100, 'intersection': ['secondary']},
    {'way_id': [5],
    'speed': 20,
    'length': 100,
    'intersection': ['service', 'service']}]

    Args:
         H: Networkx Graph object
         nodes: tuple of source and target nodes
    Returns:
         List of edges
         
    """
    edges = []
    for path in sorted(nx.all_simple_edge_paths(G, nodes[0], nodes[1])):
        for i in path:
            edges.append(G[i[0]][i[1]])
            
    return edges