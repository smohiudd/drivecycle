import math

def velocity_distance_profile(vi=0,v_target=13,vf=0,di=0,df=100,ti=0,a_max=1,step=0.1):

    """Create velocity and distance profile given, vi, vf, vtarget, amax and d

    Args:
         vi: initial velocity for segment
         v_target: target velocity for segment
         vf: final velocity for segment
         di: initial distance
         df: final distance
         ti: initial time
         a_max: maximum acceleration
         step: time step
    Returns:
         List of time, velocity and position tuple: (t,v,q)
    """

    t=ti
    z=[]

    if (df-di)*a_max > (pow(v_target,2)-((pow(vi,2)+pow(vf,2))/2)):
        
        Ta = (v_target - vi)/a_max
        Td = (v_target - vf)/a_max
        T = ti+((df-di)/v_target)+((v_target/(2*a_max))*pow((1-(vi/v_target)),2)) \
            + ((v_target/(2*a_max))*pow((1-(vf/v_target)),2))
        
        while t<=T:
            if t>=ti and t<ti+Ta and Ta!=0:
                v = vi + ((v_target-vi)/Ta)*(t-ti)
                q = di + (vi*(t-ti)) + (((v_target-vi)/(2*Ta))*pow((t-ti),2))
            elif t>=ti+Ta and t<T-Td:
                v = v_target
                q = di + (vi*(Ta/2)) + (v_target*(t-ti-(Ta/2)))
            elif t>=T-Td and t<=T:
                v = vf + ((v_target-vf)/Td)*(T-t)
                q = df - (vf*(T-t)) - (((v_target-vf)/(2*Td))*pow((T-t),2))
            elif Ta==0:
                v = v_target
                q=di+(v_target*t)
            else:
                v=None
                q=None
            
            if v<0.1:
                v=0
            z.append((t,v,q))
            t+=step
        
    else:
        vlim = math.sqrt(((df-di)*a_max)+((pow(vi,2)+pow(vf,2))/2))
        Ta = (vlim-vi)/a_max
        Td = (vlim-vf)/a_max
        T = ti+Ta+Td
        
        while t<=T:
            if t>=ti and t<ti+Ta:
                v = vi + ((vlim-vi)/Ta)*(t-ti)
                q = di + (vi*(t-ti)) + (((vlim-vi)/(2*Ta))*pow((t-ti),2))
            elif t>=ti+Ta and t<=T and Td!=0:
                v = vf + ((vlim-vf)/Td)*(T-t)
                q = df - (vf*(T-t)) - (((vlim-vf)/(2*Td))*pow((T-t),2))
            elif Td==0:
                v = vf
                q=di+(df*t)
            else:
                v=None
                q= None
                
            if v<0.1:
                v=0
            z.append((t,v,q))
            t+=step
    
    return z