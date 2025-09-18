# main sim file

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


class PTZ_Sim(object):
    def __init__(self, T, sr = 30):
        self.sample_rate = sr # in hz
        self.simTime = T # in seconds
        self.tvector = np.arange(0,T, 1/self.sample_rate)
        
        self.N = np.size(self.tvector)
        self.trajectory = np.zeros((self.N,3))
        self.trajectory[:,0] = np.cos(self.tvector) + np.random.normal(0,.05,self.N)
        self.trajectory[:,1] = .5*np.sin(self.tvector) + np.random.normal(0,.05,self.N)
        
        self.detected = [False] * self.N
        
        self._nvecs = None
        
    def plot_init(self,ax):
        # plot global frame axes
        ax.plot([0,1],[0,0],[0,0],'r')
        ax.plot([0,0],[0,1],[0,0],'b')
        ax.plot([0,0],[0,0],[0,1],'y')
        ax.plot([0],[0],[0],'ro')
        
    def is_detected(self,i,cam):
        """_summary_

        Args:
            t (_type_): _description_
            cam (PTZ_Camera): _description_
        """
        c0 = cam.position
        carpos = cam.RCI @ (self.trajectory[i,:] - c0) # expressed in camera frame

        r1,r2,r3,r4 = cam.fov_rays # these are in C frame
        
        # TODO: orient normal vectors in right order
        n1 = np.cross(r1,r2)
        n2 = np.cross(r2,r3)
        n3 = np.cross(r3,r4)
        n4 = np.cross(r4,r1)
        
        nvecs = [n1,n2,n3,n4]
        self._nvecs = nvecs
        
        for nvec in nvecs:
            if np.dot(nvec,carpos) <=0:
                return False
        
        return True
    
    def run(self,cam):
        # main loop for sim
        
        
        for k in range(self.N):
            currtime = self.tvector[k]
            if self.is_detected(k,cam):
                self.detected[k] = self.trajectory[k]
                
        return
    
        
    def animate(self,fig,ax):
        # plots timehistory; all data is generated before, this function just animates/replays it
        # Plot elements: line for path, point for particle
        line, = ax.plot([], [], [], lw=2, color="blue", ls = ':')
        point, = ax.plot([], [], [], "ro")
        
        x,y,z = self.trajectory.T
    
        # Initialization function
        def init():
            line.set_data([], [])
            line.set_3d_properties([])
            point.set_data([], [])
            point.set_3d_properties([])
            return line, point

        # Update function
        def update(frame):
            
            
            ax.set_title(f"Time: {round(self.tvector[frame],2)} seconds")
            
            # Up to current frame
            line.set_data(x[:frame], y[:frame])
            line.set_3d_properties(z[:frame])

            # Current particle position
            point.set_data([x[frame]], [y[frame]])
            point.set_3d_properties([z[frame]])
            
            return line, point

        # Animate
        ani = animation.FuncAnimation(
            fig, update, frames=len(x), init_func=init,
            interval=20, blit=False
        )
        
        return ani
    
    def get_fov_nvecs(self):
        return self._nvecs
