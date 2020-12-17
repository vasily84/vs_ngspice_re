import numpy as np
import numba
import scipy.optimize as spo
import json

from vs_utils import uuid_str
from vs_ClassObject import ClassObject
import vs_globals as G
import vs_Signal
import vs_plot


# pylint: disable=E1101 # игнор линтинга numpy

class ClassModel(ClassObject):
    def __init__(self):
        super().__init__()

class ClassModel_R(ClassModel):
    def __init__(self, R1=100):
        super().__init__()
        self.R1 = R1
        self.Xi_values = [R1]
        self.Xi_bounds = [(1e-2*G.small_R,None)]
        self.kind = 'R'

    def to_list(self):
        json_list = {"model_type":"R","R1":self.R1}
        return json_list

    def from_list(self,json_list):
        self.R1 = json_list["R1"]
   
    def setXi(self,Xi):
        self.R1 = Xi[0]

    def evaluate_model(self,VCSignal):
        VCSignal.Currents = VCSignal.Voltages/self.R1

    def init_starts_from_signal(self,VCSignal):
        """найти НУ для схемы исходя из сигнала"""
        self.R1 = 200 #!! # еще не реализовано


class ClassModel_Rphase(ClassModel):
    def __init__(self, R1=100,phase=0):
        super().__init__()
        self.R1 = R1
        self.phase = phase # сдвиг фазы считается в точках в наборе  
        self.Xi_values = [R1, phase]
        self.Xi_bounds = None #[(1e-2*G.small_R, None)]
        self.kind = 'Rphase'

    def to_list(self):
        json_list = {"model_type":"Rphase","R1":self.R1,"phase":self.phase}
        return json_list

    def from_list(self,json_list):
        self.R1 = json_list["R1"]
        self.phase = json_list["phase"]
   
    def setXi(self,Xi):
        self.R1 = Xi[0]
        self.phase = Xi[1]

    def evaluate_model(self,VCSignal):
        buf = np.empty_like(VCSignal.Voltages)
        buf = VCSignal.Voltages/self.R1
        #фазовый сдвиг, ток запаздывает за напряжением
        Nshift = -int(self.phase)
        if Nshift==0:
            VCSignal.Currents[:]=buf[:]
        else:
            VCSignal.Currents[Nshift:] = buf[:-Nshift]
            VCSignal.Currents[:Nshift] = buf[-Nshift:]

    def init_starts_from_signal(self,VCSignal):
        """найти НУ для схемы исходя из сигнала"""
        self.R1 = 200 #!! # еще не реализовано


class ClassModel_RD(ClassModel):
    def __init__(self,R2=100):
        super().__init__()
        self.R2 = R2
        self.Xi_values = [R2]
        self.Xi_bounds = [(1e-2*G.small_R,None)]
        self.kind = 'RD'

    def to_list(self):
        json_list = {"model_type":"RD","R2":self.R2}
        return json_list

    def from_list(self,json_list):
        self.R2 = json_list["R2"]

    def setXi(self,Xi):
        self.R2 = Xi[0]

    @staticmethod
    @numba.njit
    def _evaluate_model(R2,volt,curr):
        # переписать #
        curr[:] = 0.
        for i in range(len(volt)):
            v = volt[i]
            if v>=G.DIODE_VOLTAGE:
                curr[i] = (v-G.DIODE_VOLTAGE)/R2

    def evaluate_model(self,VCSignal):
        return self._evaluate_model(self.R2,VCSignal.Voltages,VCSignal.Currents)

        
class ClassModel_DR(ClassModel):
    def __init__(self, R3=100):
        super().__init__()
        self.R3=R3
        self.Xi_values = [R3]
        self.Xi_bounds = [(1e-2*G.small_R,None)]
        self.kind = 'DR'

    def to_list(self):
        json_list = {"model_type":"DR","R3":self.R3}
        return json_list

    def from_list(self,json_list):
        self.R3 = json_list["R3"]

    def setXi(self,Xi):
        self.R3 = Xi[0]

    @staticmethod
    @numba.njit
    def _evaluate_model(R3,volt,curr):
        # переписать #
        curr[:] = 0.
        for i in range(len(volt)):
            v = volt[i]
            if v<=-G.DIODE_VOLTAGE:
                curr[i] = (v+G.DIODE_VOLTAGE)/R3
    
    def evaluate_model(self,VCSignal):
        return self._evaluate_model(self.R3,VCSignal.Voltages,VCSignal.Currents)
        
class ClassModel_R1R2R3(ClassModel):
    def __init__(self, R1=100,R2=100,R3=100):
        super().__init__()
        self.R1=R1
        self.R2=R2
        self.R3=R3
        self.Xi_values = [R1,R2,R3]
        self.Xi_bounds = [(1e-2*G.small_R,None),(1e-2*G.small_R,None),(1e-2*G.small_R,None)]
        self.kind = 'R1R2R3'

    def to_list(self):
        json_list = {"model_type":"R1r2r3","R1":self.R1,"R2":self.R2,"R3":self.R3}
        return json_list

    def from_list(self,json_list):
        self.R1 = json_list["R1"]
        self.R2 = json_list["R2"]
        self.R3 = json_list["R3"]

    def setXi(self,Xi):
        self.R1 = Xi[0]
        self.R2 = Xi[1]
        self.R3 = Xi[2]
 
    @staticmethod
    @numba.njit               
    def _evaluate_model(R1,R2,R3,volt,curr):
        for i in range(len(volt)):
            v = volt[i]
            curr[i] = _I_from_VR1R2R3(v,R1,R2,R3)

    def evaluate_model(self,VCSignal):
        return self._evaluate_model(self.R1,self.R2,self.R3,VCSignal.Voltages,VCSignal.Currents)

# ток через нашу упрощенную цепь - подробности см. в проекте vs_spice_solver    
@numba.njit
def _I_from_VR1R2R3(V,R1,R2,R3):
    I = V/(R2)
    V2 = R2*I
    INIT_Rcs = 0. 

    # диод VD1 открыт
    if V2>=G.DIODE_VOLTAGE:
        up_part = V*(R1+R2)-R2*G.DIODE_VOLTAGE
        down_part = R1*R2+R1*INIT_Rcs+R2*INIT_Rcs
        Id = up_part/down_part
        return Id
    
    # диод VD3 открыт
    if V2 <=-G.DIODE_VOLTAGE:
        up_part = V*(R3+R2)+R2*G.DIODE_VOLTAGE
        down_part = R3*R2+R3*INIT_Rcs+R2*INIT_Rcs
        Id = up_part/down_part
        return Id
    
    # случай, когда диоды VD1 и VD3 закрыты - просто закон ома
    return I







        

