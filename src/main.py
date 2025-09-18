%matplotlib widget
# uncomment above for jupyter integration

import numpy as np
from matplotlib import pyplot as plt
import matplotlib.animation as animation

from ptz_sim import PTZ_Sim
from ptz_cam import PTZ_Camera


if __name__ == "__main__":
    ## set simulation parameters here
    sr = 10
    T = 10 # in seconds
    e0 = np.array([np.pi/2,0,0]) # 3-1-2 representation; z axis is pointing towards imageplane
    cam = PTZ_Camera(np.array([0, 1.3, .5]), e0) # specify position and orientation
    sim = PTZ_Sim(T,sr)  
    m1 = -2
    m2 = 2

    ## set up figure and 3D axis
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    ax.set_xlim([m1,m2])
    ax.set_ylim([m1,m2])
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_aspect('equal')
    ##
    
    sim.run(cam)
    
    # for nvec in sim.get_fov_nvecs():
    #     x1,y1,z1 = cam.RCI.T @ nvec + cam.position
    #     x0,y0,z0 = cam.position
    #     ax.plot([x0,x1],[y0,y1],[z0,z1],'r--')
    
    for dp in sim.detected:
        
        if dp is not False:
            ax.plot3D(dp[0],dp[1],dp[2],'go')
    
    
    
    
    # now animate the sim
    cam.plot_init(ax,cframe=False)
    sim.plot_init(ax)

    ani = sim.animate(fig,ax)
    
    
    
    
    # ani.save('animation_drawing.gif', writer="pillow", fps=40)
    # print("Animation saved!")
