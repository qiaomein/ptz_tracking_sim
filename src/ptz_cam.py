import numpy as np


class PTZ_Camera(object):
    # for the 30x model
    def __init__(self, pos, euler):
        # camera parameters from https://ptzoptics.imagerelay.com/share/PT-4K-xx-G3-Data-Sheet
        self.position = pos
        self._fps = 60
        self._tilt_range = [-30, 90] # in degrees
        self._pan_range = [-170, 170] # in degrees
        self._tilt_speed_range = [.7, 69.9] # in degrees / second
        self._pan_speed_range = [.7, 100] # in degrees / second
        self._focal_length_range = [7.1e-3, 210e-3] # in m; smaller means larger fov (less zoom)
        self.resolution = [1920, 1080] # 1920x1080p though this is adjustable; u,v
        self._max_range = 3  #300 * 12 * .0254 # max range 300 ft converted to meters; ## car should be within this range AND in view to be tracked #TODO: undo this temp value
        self.pxsz = 2.9e-6 # in meters; pixel size of the image sensor
        self._hfov_range = [2.5,59.2] # in degrees
        self._vfov_range = [1.4,34.6] # in degrees; bigger corresponds to smaller focal length
        self.detector_size = find_detector_size([self._hfov_range[-1],self._vfov_range[-1]],self.pxsz,self._focal_length_range[0])
        ### system modeling
        
        self._command_latency = 50 # in ms; how long it takes for the ptz to being moving after receiving command
        
        # TODO: get realistic values for rotational inertia; ok it seems these values are extremely small regardless; assume velocity input then
        self._pan_J = 1e-3 
        self._tilt_J = 1e-3 # in SI units for rotational inertia
        self.mass = 1.47 # in kg
        
        self._euler = euler # use 3-1-2 representation
        self.hfov = np.deg2rad(self._hfov_range[-1])
        self.vfov = np.deg2rad(self._vfov_range[-1])
        self.focal_length = self._focal_length_range[0]
        
        
        self.RCI = euler2dcm(euler)
        
        r1 = rotation_matrix(self.vfov/2,np.array([1,0,0])) @ rotation_matrix(self.hfov/2,np.array([0,1,0])) @ np.array([0,0,self._max_range])
        r2 = rotation_matrix(-self.vfov/2,np.array([1,0,0])) @ rotation_matrix(self.hfov/2,np.array([0,1,0])) @ np.array([0,0,self._max_range])
        r3 = rotation_matrix(-self.vfov/2,np.array([1,0,0])) @ rotation_matrix(-self.hfov/2,np.array([0,1,0])) @ np.array([0,0,self._max_range])
        r4 = rotation_matrix(self.vfov/2,np.array([1,0,0])) @ rotation_matrix(-self.hfov/2,np.array([0,1,0])) @ np.array([0,0,self._max_range])

        self.fov_rays = [r1,r2,r3,r4] # in the C frame
        
        # camera intrinsics/extrinsics for P matrix
        
        fpix = self.focal_length / self.pxsz
        u0,v0 = np.array(self.resolution) / 2
        self.K = np.array([[fpix,0,-u0],[0,fpix,-v0],[0,0,1]])
        #E = np.concat((self.RCI,self.position.reshape((3,1))),axis=1)
        #self.P = K @ E # the projection matrix to multiply by homogenous inertial coordinate
        #print('\n\n',K,E)
        
        
        
        
        return
        
    def plot_init(self,ax, cframe = True):
        # plot the camera position + pole
        x,y,z = self.position
        ax.plot(x,y,z, "mo")
        ax.plot([x,x],[y,y], [0, z], "m")
        
        # plot camera axes: red,x;blue,y;yellow z
        if cframe:
            rinc = self.RCI.T @ np.array([1,0,0])
            ax.plot([x,x+rinc[0]],[y,y+rinc[1]],[z,z+rinc[2]],'r', linewidth = .3)
            
            rinc = self.RCI.T @ np.array([0,1,0])
            ax.plot([x,x+rinc[0]],[y,y+rinc[1]],[z,z+rinc[2]],'b', linewidth = .3)
            
            rinc = self.RCI.T @ np.array([0,0,1])
            ax.plot([x,x+rinc[0]],[y,y+rinc[1]],[z,z+rinc[2]],'y', linewidth = .3)
        
        # now plot the fov cone
        
        
        for ri in self.fov_rays:
            rI1 = self.position + self.RCI.T @ ri
            x1,y1,z1 = rI1
            ax.plot([x,x1],[y,y1], [z, z1], "m--")
        
        
        return
    
### general functions below

def crossProductEq(u):
    assert len(u) == 3
    u1,u2,u3 = u.reshape(3) # so wack how i need this line smh
    uCross = np.array([[0, -u3, u2],[u3, 0, -u1],[-u2, u1, 0]])
    return uCross

def rotation_matrix(phi, ahat):
    # direct implementation of euler 
    ahat = ahat.reshape(3,1)
    R = np.cos(phi) * np.eye(3) + (1-np.cos(phi)) * (ahat @ ahat.T) - np.sin(phi) * crossProductEq(ahat)

    return R

def euler2dcm(e):
    """_summary_
    Let the world (W) and body (B) reference frames be initially aligned.  In a
    3-1-2 order, rotate B away from W by angles psi (yaw, about the body Z
    axis), phi (roll, about the body X axis), and theta (pitch, about the body Y
    axis).  R_BW can then be used to cast a vector expressed in W coordinates as
    a vector in B coordinates: vB = R_BW * vW
    
        Args:
        e (_type_): _description_

    Returns:
        _type_: _description_
        
        
    """
    
    a1 = np.array([0, 0, 1])
    a2 = np.array([1, 0, 0])
    a3 = np.array([0,1,0])
    
    phi,theta,psi = e
    
    RBW = rotation_matrix(theta,a3) @ rotation_matrix(phi,a2) @ rotation_matrix(psi,a1)
    return RBW
    

def find_detector_size(hvfov,pxsz,f): # hvfov is [hfov,vfov] in degrees
    # based on this: https://www.phase1vision.com/userfiles/product_files/imx485lqj_lqj1_flyer.pdf
    # https://wavelength-oe.com/optical-calculators/field-of-view/
    
    # returns w,h of image sensor dimensions
    hfov,vfov = hvfov
    ds = np.array([2*f* np.tan(np.deg2rad(hfov)/2), 2*f* np.tan(np.deg2rad(vfov)/2)])
    print ("Camera image sensor is ", ds, np.linalg.norm(ds))
    return ds