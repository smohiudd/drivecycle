Valhalla Map Matching
=========================

To generate complete drive cycles for bus routes we can utilize the open routing engine `Valhalla <https://valhalla.readthedocs.io/en/latest/>`_ to 
match route shapes to OSM ways. Valhalla has a `map matching API <https://valhalla.readthedocs.io/en/latest/api/map-matching/api-reference/>`_ and we use the trace attributes call
to get detailed information (attributes) along the route. The repsonse is a path graph which includes 
sectoins of way_ids along with details such as speed, road class and node intersecting edge road class.

This information is critical to develop drivecycle profile along the route taking into account speed 
and stop locations. 

An example POST request to the API may look somehting like this:

.. code-block:: python

    {
        "encoded_polyline":"gfqb`BvlijxE...",
        "costing":"auto",
        "filters":
            {
                "attributes":[
                    "edge.way_id",
                    "edge.names",
                    "edge.length",
                    "edge.speed",
                    "node.intersecting_edge.road_class",
                    "node.intersecting_edge.begin_heading",
                    "node.elapsed_time",
                    "node.type"],
                "action":"include"
            }
    }

The resulting reponse would return detailed infomatoin about the route:

.. code-block:: python

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

Unforunately, the resulting path graph has a high proportion of short edges which do not work well
with the trajectory algorithm so we must consolidate nodes to simplify the graph:

.. code-block:: python

    g = graph.Graph(data_)

    # Cluster intersections in the filter list that 
    # are close together
    a.consolidate_intersections(filters = ["tertiary", "secondary"])

    # Merge adjacent edges that have the same speed but do not merge
    # intersections in the filter list. We want to maintain these
    # intersections as stop locations.
    a.simplify_graph(filters=["tertiary", "secondary"])

Running the simplification step should drastically reduce the number of edges in the path graph. 