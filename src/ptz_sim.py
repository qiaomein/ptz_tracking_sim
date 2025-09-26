# main sim file
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation



class PTZ_Sim(object):
    def __init__(self, T, trajectory_file = None, sampling_rate = 30):
        self.sample_rate = sampling_rate # in hz
        self.simTime = T # in seconds
        self.tvector = np.arange(0,T, 1/self.sample_rate)
        
        self.N = np.size(self.tvector)
        self.trajectory = np.zeros((self.N,3)) # inspo: https://mathworld.wolfram.com/LissajousCurve.html
        # self.trajectory[:,0] = .75*np.cos(3*self.tvector) + np.random.normal(0,.02,self.N)
        # self.trajectory[:,1] = .5*np.sin(self.tvector) + np.random.normal(0,.02,self.N)
        
        if trajectory_file is None:
            self.trajectory[:,0] = .75*np.cos(self.tvector) + np.random.normal(0,.02,self.N)
            self.trajectory[:,1] = .75*np.sin(self.tvector) + np.random.normal(0,.02,self.N)
        else:
            print(f"{trajectory_file} found. Overriding sampling rate...")
            ct = pd.read_csv(trajectory_file)
            # look at car 0
            ct = ct[ct['car_id'] == 0]
            ctx,ctz,cty = ct.x.to_numpy(), -ct.y.to_numpy(), -ct.z.to_numpy()
            self.tvector = ct.timestamp.to_numpy()
            self.tvector -= self.tvector[0]
            
            
            dti = 20
            self.tvector = self.tvector[::dti]
            self.N = np.size(self.tvector)
            self.trajectory = np.zeros((self.N,3))
            self.trajectory[:,0] = ctx[::dti]
            self.trajectory[:,1] = cty[::dti]
            self.trajectory[:,2] = ctz[::dti]
            
            
            
            
        
        self.cam_history_3D = [None] * self.N # track all detected points
        self.cam_history_2D = np.zeros((self.N,2)) # track what the camera sees
        
        self._nvecs = None
        
    def plot_init(self,ax):
        # plot global frame axes
        ax.plot([0,1],[0,0],[0,0],'r')
        ax.plot([0,0],[0,1],[0,0],'b')
        ax.plot([0,0],[0,0],[0,1],'y')
        ax.plot([0],[0],[0],'ro', markersize=1)
        
        # plot track
        side_l = pd.read_csv('..//data//side_l.csv', header=None, names=['x', 'y', 'z', 'dist'])
        side_r = pd.read_csv('..//data//side_r.csv', header=None, names=['x', 'y', 'z', 'dist'])
        
        ax.plot(side_l['x'], side_l['z'], -side_l['y'], 'gray', linewidth=1, label='Track')
        ax.plot(side_r['x'], side_r['z'], -side_r['y'],'gray', linewidth=1)
    def is_detected(self,i,cam):
        """_summary_

        Args:
            t (_type_): _description_
            cam (PTZ_Camera): _description_
        """
        c0 = cam.position
        carpos = cam.RCI @ (self.trajectory[i,:] - c0) # expressed in camera frame

        r1,r2,r3,r4 = cam.fov_rays # these are in C frame
        
        # ensure all nvecs are pointed towards inside of fov pyramid
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
                self.cam_history_3D[k] = self.trajectory[k]
                
                camcoord = cam.K @ ((cam.RCI @ (self.trajectory[k]-cam.position)))
                camcoord /= camcoord[-1]
                u,v = camcoord[0],camcoord[1]
                self.cam_history_2D[k] = np.array([u,v])
                
                
                
                
        return
    
        
    def animate(self,fig,ax, cam_ax, save = True):
        # plots timehistory; all data is generated before, this function just animates/replays it
        # Plot elements: line for path, point for particle
        
        line, = ax.plot([], [], [], lw=2, color="blue", ls = ':')
        point, = ax.plot([], [], [], "ko", markersize = 7)
        point_c, = cam_ax.plot([], [], "ro") 
        
        x,y,z = self.trajectory.T
        
    

        # Update function
        def update(frame):
            
            
            ax.set_title(f"Time: {round(self.tvector[frame],2)} seconds")
            
            # Up to current frame
            line.set_data(x[:frame], y[:frame])
            line.set_3d_properties(z[:frame])

            # Current particle position
            point.set_data([x[frame]], [y[frame]])
            point.set_3d_properties([z[frame]])
            
            # update cam view
            u,v = self.cam_history_2D[frame]
            if u != 0 and v !=0:
                point_c.set_data([u],[v])
            
            return line, point, point_c

        # Animate
        ani = animation.FuncAnimation(
            fig, update, frames=len(x),
            interval=20, blit=False
        )
        
        if save:
            ani.save("..//ptz_sim.gif", writer="pillow", fps=40)
            print("Animation saved!")
        
        return ani
    
    
    def get_fov_nvecs(self):
        return self._nvecs
