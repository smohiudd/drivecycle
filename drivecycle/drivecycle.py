import numpy as np
from transit_drivecycle import velocity

def get_drivecycle(edges,di=0,vi=0,ti=0,a_max=1,stops=None, step=0.1, stop_at_node=False, kmh=True):

    """Create drivecycle given vehicle path edge list

    Args:
         edges: list of dictionaries with with way_id, speed, length (m) and intersection keys
         di: initial distance of path
         ti: initial time
         a_max: maximum acceleration
         stops: dictionary of intersection to stop at and for how max number of seconds. i.e. {"bus_stop":30,"primary":10}
         stop_at_node: if the vehicle should stop at the intersections specified in stops
         kmh: speed values in edges are in km/h
    Returns:
         List of time, velocity and position tuple: (t,v,q)
    """

    c = np.array([(0,0,0)])
    stop = None
    conversion = 1000/3600

    for i in range(len(edges)):
        
        if kmh==True:
            conversion = 1000/3600
        else:
            conversion = 1

        try:
            v_target_next = edges[i+1]["speed"]*conversion
        except:
            v_target_next = 0

        v_target = edges[i]["speed"]*conversion
        df = di+edges[i]["length"]
        
        
        if any(x in list(stops.keys()) for x in edges[i]["intersection"]) and stop_at_node==True:
            stop = np.random.randint(2)
        
        if stop:
            vf=0
        else:
            if v_target_next >= v_target:
                vf = v_target
            else:
                vf = v_target_next
        
        d = velocity.velocity_distance_profile(vi=vi,v_target=v_target,vf=vf,di=di,df=df,ti=ti,a_max=a_max,step=step)
        
        # if len(d)==0:
        #     continue
        
        if stop:

            stop_max_time = stops[edges[i]["intersection"][0]]
            stop_time = np.random.randint(5,stop_max_time)
            
            x = np.linspace(d[-1][0],d[-1][0]+stop_time,5)
            v = np.zeros(5)
            q = np.repeat(d[-1][2],5)
            s = np.column_stack((x,v,q))
            d = np.concatenate([d, s])
        
        c = np.concatenate([c, d])

        di = c[-1][2]
        ti = d[-1][0]
        vi=d[-1][1]
        stop = 0

    return c