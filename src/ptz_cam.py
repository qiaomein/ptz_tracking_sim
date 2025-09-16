import numpy as np


class PTZ_Camera(object):
    # for the 30x model
    def __init__(self, pos):
        # camera parameters
        self.position = pos
        self._fps = 60
        self._tilt_range = [-30, 90] # in degrees
        self._pan_range = [-170, 170] # in degrees
        self._tilt_speed_range = [.7, 69.9] # in degrees / second
        self._pan_speed_range = [.7, 100] # in degrees / second
        self._focal_length_range = [7.1, 210] # in mm; smaller means larger fov (less zoom)
        self._resolution = [1920, 1080] # 1920x1080p though this is adjustable
        ### system modeling
        
        self._command_latency = 50 # in ms; how long it takes for the ptz to being moving after receiving command
        
        # TODO: get realistic values for rotational inertia; ok it seems these values are extremely small regardless; assume velocity input then
        self._pan_J = 1e-3 
        self._tilt_J = 1e-3 # in SI units for rotational inertia
        self.mass = 1.47 # in kg
        
        # camera intrinsics/extrinsics for P matrix
        
        
        return
        
    def plot_init(self,ax):
        # plot the camera position + pole
        x,y,z = self.position
        ax.plot(x,y,z, "mo")
        ax.plot([x,x],[y,y], [0, z], "m")
        
        # now plot the fov cone
        
        return
    
    