# Drive Cycle

Create a drive cycle for a transit route

### Installation

Install the package in editable mode:

```pip install -e ./```

### Import libraries

```python
from drivecycle import drivecycle, trajectory
from drivecycle.utils import plots
```

### Plot Simple Tragectories

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

```python
# What nodes should we stop at and for how long (seconds)
stop={"bus_stop":30,"tertiary":10}

# Generate route drive cycle
route_drive_cycle = drivecycle.get_drivecycle(path, stops=stop, stop_at_node=True, step=1)
```

#### Velocity - Distance Plot

![VD-Plot](/images/drivecycle_vd.png)

##### Velocity - Time Plot

![VT-Plot](/images/drivecycle_vt.png)

##### Distance - Time Plot

![DT-Plot](/images/drivecycle_dt.png)

#### Sample input

A path graph is created using OpenStreetMap (OSM) taxonomy. `intersection` denotes end node intersect edge type as used in OSM. For example `"intersection":["primary"]` indicates a primary road intersecting the end node.

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

### Generate path graph from input

```python

stops=[100,367] #linearly referenced stop locations

route_graph = utils.Graph(edges)


#We simplify the graph by merging adjacent edges with the same speed
simplified_route_graph = route_graph.simplify_graph()

graph_with_stops = utils.include_stops(simplified_route_graph,stops)
```