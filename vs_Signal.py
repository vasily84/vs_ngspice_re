import numpy as np
import scipy.fft as scf
import math
import vs_globals as G

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

    def scalar_cmp_L(self,baseSignal):
        """скалярное сравнение сигналов"""
        sub = np.copy(self.Currents)
        sub = sub-baseSignal.Currents
        sub = np.abs(sub)
        N = len(baseSignal.Currents)
        norm1 = np.max(baseSignal.Currents)-np.min(baseSignal.Currents)

        return math.fsum(sub)/(N*norm1)

    def scalar_cmp_L2(self,baseSignal):
        """скалярное сравнение сигналов"""
        sub = np.copy(self.Currents)
        sub = sub-baseSignal.Currents
        N = len(baseSignal.Currents)
        norm1 = np.max(baseSignal.Currents)-np.min(baseSignal.Currents)
        return math.fsum(sub*sub)/(N*N*norm1*norm1)

    def scalar_cmp(self,baseSignal):
        return self.scalar_cmp_L(baseSignal)

    def get_loss_row(self,baseSignal):
        return [self.scalar_cmp_L(baseSignal),self.scalar_cmp_L2(baseSignal)]
    
    def get_features_row(self):
        """ измерить признаки сигнала """
        N = len(self.Currents) # число отсчетов
        csumm = math.fsum(self.Currents)/N # сумма токов
        c2summ = math.fsum(self.Currents**2)/(N*N) # сумма квадратов токов
        cmax = np.max(self.Currents)
        cmin = np.min(self.Currents)
        row = [cmax,cmin,csumm,c2summ]
        harmonics = scf.rfft(self.Currents)

        for i in range(5): # добавляем первые 5 гармоник
            value_i = np.abs(harmonics[i])
            angle_i = np.angle(harmonics[i])
            row.append(value_i)
            row.append(angle_i)
        
        return row



