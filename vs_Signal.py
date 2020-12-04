import numpy as np
import vs_globals as G
import math

class ModelSignal():
    def __init__(self, title=''):
        self.Voltages = np.zeros(G.signal_POINT_COUNT)
        self.Currents = np.zeros_like(self.Voltages)
        self.initWave() 
        self.Title = title 
    
    def initWave(self,V=G.signal_Voltage,dt=G.signal_dt ):
        p = G.signal_POINT_COUNT
        wtime = np.linspace(0,2.*np.pi,p,False)
        self.Voltages = V*np.sin(wtime)
        self.Currents = np.zeros_like(self.Voltages)

    def copy(self,VCsignal):
        self.Voltages = np.copy(VCsignal.Voltages)
        self.Currents = np.copy(VCsignal.Currents)

    def load(self,fileName):
        fileData = np.load(fileName)
        self.Voltages = fileData['Voltages']
        self.Currents = fileData['Currents']

    def save(self,fileName):
        np.savez(fileName,Voltages=self.Voltages,Currents=self.Currents)

    def scalar_cmp_L(self,signal2):
        """скалярное сравнение сигналов"""
        sub = np.copy(self.Currents)
        sub = sub-signal2.Currents
        sub = np.abs(sub)
        return math.fsum(sub)/len(signal2.Currents)

    def scalar_cmp_L2(self,signal2):
        """скалярное сравнение сигналов"""
        sub = np.copy(self.Currents)
        sub = sub-signal2.Currents
        N = len(signal2.Currents)
        return math.fsum(sub*sub)/(N*N)

    def scalar_cmp(self,signal2):
        return self.scalar_cmp_L(signal2)

