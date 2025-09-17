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
        self.trajectory[:,1] = np.sin(self.tvector) + np.random.normal(0,.05,self.N)
        
    def plot_init(self,ax):
        # plot global frame axes
        ax.plot([0,1],[0,0],[0,0],'r')
        ax.plot([0,0],[0,1],[0,0],'b')
        ax.plot([0,0],[0,0],[0,1],'y')
        ax.plot([0],[0],[0],'ro')
    
