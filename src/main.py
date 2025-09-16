import numpy as np
from matplotlib import pyplot as plt
import matplotlib.animation as animation

from ptz_sim import PTZ_Sim
from ptz_cam import PTZ_Camera




if __name__ == "__main__":
    sr = 12
    T = 5 # in seconds
    cam = PTZ_Camera(np.array([0, 1.3, .5]))
    sim = PTZ_Sim(T,sr)  
    m1 = -2
    m2 = 2

    # Set up figure and 3D axis
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    ax.set_xlim([m1,m2])
    ax.set_ylim([m1,m2])
    ax.set_aspect('equal')
    
    
    x,y,z = sim.trajectory.T
    
   
    
    

    # Plot elements: line for path, point for particle
    line, = ax.plot([], [], [], lw=2, color="blue", ls = ':')
    point, = ax.plot([], [], [], "ro")
    cam.plot_init(ax)

    
    
    
    
    
    
    # Initialization function
    def init():
        line.set_data([], [])
        line.set_3d_properties([])
        point.set_data([], [])
        point.set_3d_properties([])
        return line, point

    # Update function
    def update(frame):
        # Up to current frame
        line.set_data(x[:frame], y[:frame])
        line.set_3d_properties(z[:frame])

        # Current particle position
        point.set_data(x[frame], y[frame])
        point.set_3d_properties(z[frame])
        return line, point

    # Animate
    ani = animation.FuncAnimation(
        fig, update, frames=len(x), init_func=init,
        interval=20, blit=True
    )

    #plt.show()
    ani.save('animation_drawing.gif', writer='imagemagick', fps=30)