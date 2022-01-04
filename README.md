# Drive Cycle

*Drive Cycle* is python library that can be used to simulate trajectories (i.e. drive cycles) for public transit buses which can then be used for tasks like energy consumption simluations. 

### Installation

Install the package in editable mode:

```pip install -e ./```

### Import libraries

```python
from drivecycle import drivecycle, trajectory
from drivecycle.utils import plots
```

### Plot Simple Tragectories

The 'Trajectory' class can be used to generate a trajectory given some contraints such as distance, acceleration and start/end/target velocities. The current release only models constant acceleration trajectories however other models may be added in future. 

```python
traj = trajectory.Trajectory(vi=5, v_target=12, vf=8, di=0, df=150, step=0.1)
traj_values = traj.const_accel(a_max=1).get_trajectory()

plots.plot_vt(traj_values, "plot_vt.png")
```

##### Velocity - Distance Plot

![VD-Plot](/images/plot_vd.png)

##### Velocity - Time Plot

![VT-Plot](/images/plot_vt.png)

##### Distance - Time Plot

![DT-Plot](/images/plot_dt.png)


### Generate Drive Cycle

Trajectories are grouped together to form drive cycles of given path. See [sample](#sample-path-input) drive cycle input path. The `Drivecycle` class may include a `stops` parameter which constrains which nodes (i.e. street interseciton or bus stops) the vehicle must stop at and for how long. 

```python
# What nodes should we stop at and for how long (seconds)
stop={"bus_stop":30,"tertiary":10}

# Generate route drive cycle
route_drive_cycle = drivecycle.get_drivecycle(path, stops=stop, stop_at_node=True, step=0.1)
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

Drive Cycle include utils that can used to generate graphs usting `networkx`. These are helpful to simplify path graphs to reduce redundant nodes and edges that may break the `Trajectory` or `Drivecycle` classes. It can also be used to embed stop in a give path graph. 

```python

stops=[100,367] #linearly referenced stop locations

route_graph = utils.Graph(edges)


#We simplify the graph by merging adjacent edges with the same speed
simplified_route_graph = route_graph.simplify_graph()

graph_with_stops = utils.include_stops(simplified_route_graph,stops)
```