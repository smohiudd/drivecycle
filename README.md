# Drive Cycle

*Drive Cycle* is python library that can be used to simulate trajectories (i.e. drive cycles) for public transit buses which can then be used for tasks like energy consumption simluations. 

### Installation

Install the package in editable mode:

```pip install -e ./```

### Import libraries

```python
from drivecycle import drivecycle, trajectory, utils, plots
```

### Plot Simple Tragectories

The `Trajectory` class can be used to generate a trajectory given some contraints such as distance, acceleration and start/end/target velocities. This current release only models constant acceleration trajectories however other models may be added in future. 

```python
traj = trajectory.const_accel(vi=5, v_target=12, vf=8, di=0, df=150, step=0.1)

plots.plot_vt(traj, "plot_vt.png")
```

##### Velocity - Distance Plot

![VD-Plot](/images/plot_vd.png)

##### Velocity - Time Plot

![VT-Plot](/images/plot_vt.png)

##### Distance - Time Plot

![DT-Plot](/images/plot_dt.png)


### Generate Drive Cycle

Trajectories are grouped together to form drive cycles of a given path. See [sample](#sample-path-input) drive cycle input path. The `Drivecycle` class may include a `stops` parameter that constrains which nodes (i.e. street interseciton or bus stops) the vehicle must stop at and for how long. 

```python
# What nodes should we stop at and for how long (seconds)
stop={"bus_stop":30,"tertiary":10}

# Generate route drive cycle
route_drive_cycle = drivecycle.sequential(edges, stops=stop, stop_at_node=True, step=0.1)
```

#### Velocity - Distance Plot

![VD-Plot](/images/drivecycle_vd.png)

##### Velocity - Time Plot

![VT-Plot](/images/drivecycle_vt.png)

##### Distance - Time Plot

![DT-Plot](/images/drivecycle_dt.png)

### Sample Path Input

A path graph data structure is created using OpenStreetMap (OSM) taxonomy. `intersection` denotes the edge that intersects the end node and may be another OSM `way` or simply a bus stop. For example `"intersection":["primary"]` indicates a primary road intersecting the end node. 

```python
path = [
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
        "speed":20,
        "length":100,
        "intersection":["bus_stop"]
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
        "intersection":["tertiary"]
    },
    {
        "way_id":5,
        "speed":20,
        "length":100,
        "intersection":["service","service"]
    }
]

```

### Generate Path Graph

Drive Cycle include utils that can used to generate graphs usting `networkx`. These are helpful to simplify path graphs to reduce redundant nodes and edges that may cause trajectories to fail. It can also be used to embed stops in a given path graph. 

```python

stops=[100,367] #linearly referenced stop locations

route_graph = utils.Graph(edges)

route_graph.include_stops(stops)
route_graph.consolidate_intersections(["tertiary", "secondary", "bus_stop"])
route_graph.simplify_graph(["tertiary", "secondary", "bus_stop"])

route_graph.get_edges()

```

### Generate Drivecycle using Valhalla Trace Attributes

Valhalla's [map matching API](https://valhalla.readthedocs.io/en/latest/api/map-matching/api-reference/) can be used to match a bus route geometry to OSM way ids. This can help us determine both road speeds and intersection locations along a route. Using the map matching Trace Attributes action, we can get a list of OSM edges the bus route travels along:

```python
[{'end_node': {'type': 'street_intersection',
   'elapsed_time': 0.698,
   'intersecting_edges': [{'road_class': 'service_other',
     'begin_heading': 204,
     'to_edge_name_consistency': False,
     'from_edge_name_consistency': False}]},
  'length': 0.007,
  'names': ['48 Avenue NW'],
  'speed': 35,
  'way_id': 463682703},
 {'end_node': {'type': 'street_intersection',
   'elapsed_time': 7.607,
   'intersecting_edges': [{'road_class': 'residential',
     'begin_heading': 131,
     'to_edge_name_consistency': False,
     'from_edge_name_consistency': False}]},
  'length': 0.067,
  'names': ['48 Avenue NW'],
  'speed': 35,
  'way_id': 463682703}
  .
  .
  .
  ```

Using the drivecycle apis listed above we can then generate a simulation drivecycle of the entire route:

![DT-Plot](/images/route_drivecycle.png)
