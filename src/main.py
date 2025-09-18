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
    T = 12 # in seconds
    e0 = np.array([np.pi/2+np.pi/16,0,0]) # 3-1-2 representation; z axis is pointing towards imageplane
    cam = PTZ_Camera(np.array([0, 1.7, .5]), e0) # specify position and orientation
    sim = PTZ_Sim(T,sr)  
    m1 = -2
    m2 = 2

    ## set up figure for 3d sim
    fig = plt.figure(figsize=(7,7))
    ax = fig.add_subplot(111, projection="3d")
    ax.set_xlim([m1,m2])
    ax.set_ylim([m1,m2])
    ax.set_zlim([0,3])
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_aspect('equal')
    ## now setup figure for camera view
    cfig, axc = plt.subplots()
    axc.set_title("Camera Display")
    
    # axc.set_xlim([0,cam.resolution[0]])
    # axc.set_ylim([0,cam.resolution[1]])
    
    # run the simulation
    sim.run(cam)
    
    
    
    
    
    ## handle plotting/animation
    
    # for nvec in sim.get_fov_nvecs():
    #     x1,y1,z1 = cam.RCI.T @ nvec + cam.position
    #     x0,y0,z0 = cam.position
    #     ax.plot([x0,x1],[y0,y1],[z0,z1],'r--')
    
    # plot all detected points
    for dp in sim.detected:
        
        if dp is not False:
            ax.plot3D(dp[0],dp[1],dp[2],'go',markersize = 3)
            camcoord = cam.K @ ((cam.RCI @ dp) - cam.position)
            print(camcoord[-1])
            camcoord /= camcoord[-1]
            u,v = camcoord[0],camcoord[1]
            axc.plot(u,v,'ro')
    
    
    
    
    # now animate the sim
    cam.plot_init(ax)
    sim.plot_init(ax)

    ani = sim.animate(fig,ax, save = False)
    