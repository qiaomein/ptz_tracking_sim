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
        self.trajectory[:,0] = np.cos(self.tvector)
        self.trajectory[:,1] = np.sin(self.tvector)
        
    def plot_trajectory(self):
        plt.figure()
        pass
    
