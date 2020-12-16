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
        # функции меры, которая используется в скалярной оптимизации
        #self.scalar_cmp = self.scalar_cmp_xy
        self.scalar_cmp = self.scalar_cmp_L2
    
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

    def scalar_cmp_xy(self,baseSignal):
        N = len(self.Currents)
        norm_c = np.max(baseSignal.Currents)-np.min(baseSignal.Currents)
        norm_v = np.max(baseSignal.Voltages)-np.min(baseSignal.Voltages)

        # расстояние в пространстве между точками
        def Lij1(i,j):
            v1 = self.Voltages[i]
            c1 = self.Currents[i]
            v2 = baseSignal.Voltages[j]
            c2 = baseSignal.Currents[j]
            res = np.sqrt(((v1-v2)/norm_v)**2+((c1-c2)/norm_c)**2)
            return res

        # вычисляем сумму по наиболее близким
        used_jj = set()
        minSumSeries = np.zeros_like(self.Currents)
        for i in range(N):
            setJ = (set(range(N))-used_jj)
            j0 = setJ.pop()
            setJ.add(j0)
            Lmin = Lij1(i,j0)
            j_min = j0
            for j in setJ:                 
                if Lij1(i,j) <Lmin:
                    Lmin = Lij1(i,j)
                    j_min = j

            used_jj.add(j_min)
            minSumSeries[i] = Lmin

        return math.fsum(minSumSeries)

    
    def scalar_cmp_xy2(self,baseSignal):
        """вычислить функцию потерь для шумного сигнала."""
        N = len(self.Currents)
        norm_c = np.max(baseSignal.Currents)-np.min(baseSignal.Currents)
        norm_v = np.max(baseSignal.Voltages)-np.min(baseSignal.Voltages)
        
        # расстояние в пространстве между точками
        def Lij2(i,j):
            v1 = self.Voltages[i]
            c1 = self.Currents[i]
            v2 = baseSignal.Voltages[j]
            c2 = baseSignal.Currents[j]
            res = ((v1-v2)/norm_v)**2+((c1-c2)/norm_c)**2
            return res

        # вычисляем сумму по наиболее близким
        used_jj = set()
        minSumSeries = np.zeros_like(self.Currents)
        for i in range(N):
            setJ = (set(range(N))-used_jj)
            j0 = setJ.pop()
            setJ.add(j0)
            Lmin = Lij2(i,j0)
            j_min = j0
            for j in setJ:                 
                if Lij2(i,j) <Lmin:
                    Lmin = Lij2(i,j)
                    j_min = j

            used_jj.add(j_min)
            minSumSeries[i] = Lmin

        return math.fsum(minSumSeries)


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



