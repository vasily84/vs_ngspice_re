import numpy as np
import scipy.fft as scf
import math
import vs_globals as G
import numba

@numba.njit
def _scalar_cmp_xy(volt_a,curr_a,volt_b,curr_b):
    lenA = len(volt_a)
    lenB = len(volt_b)
    norm_N = min(lenA,lenB)
    norm_c = (np.max(curr_b)-np.min(curr_b))
    norm_v = (np.max(volt_b)-np.min(volt_b))
    # примитивная нормировка на '1'
    volt_a = volt_a/(norm_v*norm_N)
    volt_b = volt_b/(norm_v*norm_N)
    curr_a = curr_a/(norm_c*norm_N)
    curr_b = curr_b/(norm_c*norm_N)

    # вычисляем сумму по наиболее близким
    axis_jj = [_ for _ in range(lenB)]
    Summ = 0.

    for i in range(lenA):
        first_j = True
        for j in axis_jj:
            if j<0:
                continue    
            
            v1 = volt_a[i]
            c1 = curr_a[i]
            v2 = volt_b[j]
            c2 = curr_b[j]
            Lij = np.sqrt(((v1-v2))**2+((c1-c2))**2)
            
            if first_j:      
                Lmin = Lij
                j_min = j
                first_j = False

            elif Lij <Lmin:
                Lmin = Lij
                j_min = j

        axis_jj[j_min]=-1 # маркер уже использованного индекса
        Summ += Lmin

    return Summ


@numba.njit
def _scalar_cmp_xy2(volt_a,curr_a,volt_b,curr_b):
    lenA = len(volt_a)
    lenB = len(volt_b)
    norm_N = min(lenA,lenB)
    norm_c = (np.max(curr_b)-np.min(curr_b))
    norm_v = (np.max(volt_b)-np.min(volt_b))
    # примитивная нормировка на '1'
    volt_a = volt_a/(norm_v*norm_N)
    volt_b = volt_b/(norm_v*norm_N)
    curr_a = curr_a/(norm_c*norm_N)
    curr_b = curr_b/(norm_c*norm_N)

    # вычисляем сумму по наиболее близким
    axis_jj = [_ for _ in range(lenB)]
    Summ = 0.

    for i in range(lenA):
        first_j = True
        for j in axis_jj:
            if j<0:
                continue    
            
            v1 = volt_a[i]
            c1 = curr_a[i]
            v2 = volt_b[j]
            c2 = curr_b[j]

            Lij = (v1-v2)**2+(c1-c2)**2
            
            if first_j:      
                Lmin = Lij
                j_min = j
                first_j = False

            elif Lij <Lmin:
                Lmin = Lij
                j_min = j

        axis_jj[j_min]=-1 # маркер уже использованного индекса
        Summ += Lmin
    return Summ


class ModelSignal():
    def __init__(self, title='',Points=None):
        if Points is None:
            Points = G.signal_POINT_COUNT
        self.Voltages = np.zeros(Points)
        self.Currents = np.zeros_like(self.Voltages)
        self.initWave() 
        self.Title = title 
        # функции меры, которая используется в скалярной оптимизации
        self.scalar_cmp = self.scalar_cmp_xy2
    
    def initWave(self,V=G.signal_Voltage,dt=G.signal_dt ):
        p = len(self.Voltages)
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
        """ функция сравнения двух сигналов. линейная """
        return _scalar_cmp_xy(self.Voltages,self.Currents,baseSignal.Voltages,baseSignal.Currents)

    def scalar_cmp_xy2(self,baseSignal):
        """ функция сравнения двух сигналов. квадратичная """
        return _scalar_cmp_xy2(self.Voltages,self.Currents,baseSignal.Voltages,baseSignal.Currents)



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
        return [self.scalar_cmp_xy(baseSignal),self.scalar_cmp_xy2(baseSignal)]
    
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



