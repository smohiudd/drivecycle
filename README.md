## Drive Cycle

### Create a drive cycle for a transit route

#### Import libraries

```python 
from transit_drivecycle import drivecycle
from transit_drivecycle import utils
```

#### Sample input

```intersection``` denotes end node intersect edge type. For example ```"intersection":["primary"]``` indicates a primary road intersecting the end node.

```python 
edges = [
    {
        "way_id":1,
        "speed":20,
        "length":100,
        "intersection":["primary"]
    },
    {
        "way_id":2,
        "speed":20,
        "length":145,
        "intersection":["primary"]
    },
        {
        "way_id":3,
        "speed":50,
        "length":150,
        "intersection":["primary"]
    },
        {
        "way_id":4,
        "speed":50,
        "length":100,
        "intersection":["secondary"]
    },
    {
        "way_id":5,
        "speed":20,
        "length":100,
        "intersection":["service","service"]
    }
]
```

#### Generate graph from input

```python

stops=[100,367] #linearly referenced stop locations

route_graph = utils.Graph(edges)


#We simplify the graph by merging adjacent edges with the same speed
simplified_route_graph = route_graph.simplify_graph()

graph_with_stops = utils.include_stops(simplified_route_graph,stops) 
```

#### Generate drive cycle

```python
# What nodes should we stop at and for how long (seconds)
stop={"bus_stop":30,"tertiary":10}

# Generate route drive cycle
route_drive_cycle = drivecycle.get_drivecycle(graph_with_stops,stops=stop, stop_at_node=True, step=1)
```