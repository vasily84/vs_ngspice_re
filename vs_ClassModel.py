import numpy as np
import scipy.optimize as spo
import json

from vs_utils import uuid_str
import vs_globals as G
import vs_Signal
import vs_plot


# pylint: disable=E1101 # игнор линтинга numpy

class ClassModel():
    def run_simulation(self,VCSignal=None):
        if VCSignal is None:
            VCSignal = G.modelSignal

        self.save_model_file()
        self.evaluate_model(VCSignal)
        Noise = G.signal_CurrentNoiseAmplitude*np.random.rand(len(VCSignal.Currents))
        VCSignal.Currents = Noise+VCSignal.Currents
        VCSignal.save(self.signalFileName)
        
        row = [self.baseName]+VCSignal.get_features_row()
        row.append(self.kind)
        Loss = VCSignal.get_loss_row(G.targetSignal)
        row = row+Loss
        G.dataset.writerow(row)
        
        self.simulationResult = VCSignal


    def run_scalar_optimization(self):
        self.plt = vs_plot.InteractivePlot()
        self.plt.begin()
        self.runCounter = 0 # счетчик числа вызовов минимизируемой
        #Xres = spo.minimize(self.optimization_subroutine,self.Xi_values,bounds=self.Xi_bounds)
        Xres = spo.minimize(self.optimization_subroutine,self.Xi_values,method='Powell')
        self.plt.end()
        return Xres

    def optimization_subroutine(self,Xi):
        self.newFileName()
        self.setXi(Xi)
        self.run_simulation()
        XLoss = self.simulationResult.scalar_cmp(G.targetSignal)
        self.runCounter += 1 

        if(self.runCounter == 1): # это первый вызов
            self.minXLoss = XLoss

        if(XLoss < self.minXLoss):
            self.minXLoss = XLoss

        self.plt.plot(G.modelSignal,G.targetSignal)
            

        return XLoss
    
    def save_model_file(self):
        with open(self.fileName, 'w') as newFile:   
            json.dump(self.to_list(),newFile)   

    def load_model_from_file(self):   
        with open(self.fileName, "r") as read_file:
            json_list = json.load(read_file) 
        self.from_list(json_list)
     
    def newFileName(self):
        self.baseName = uuid_str()
        self.fileName = self.baseName+".m_json"
        self.signalFileName = self.baseName+".npz"

    def __init__(self):
        self.newFileName()
        #self.simulationResult = None

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

    def evaluate_model(self,VCSignal):
        # переписать #
        VCSignal.Currents[:] = 0.
        for i in range(len(VCSignal.Voltages)):
            v = VCSignal.Voltages[i]
            if v>=G.DIODE_VOLTAGE:
                VCSignal.Currents[i] = (v-G.DIODE_VOLTAGE)/self.R2
        
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

    def evaluate_model(self,VCSignal):
        # переписать #
        VCSignal.Currents[:] = 0.
        for i in range(len(VCSignal.Voltages)):
            v = VCSignal.Voltages[i]
            if v<=-G.DIODE_VOLTAGE:
                VCSignal.Currents[i] = (v+G.DIODE_VOLTAGE)/self.R3

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
 
    def evaluate_model(self,VCSignal):
        for i in range(len(VCSignal.Voltages)):
            v = VCSignal.Voltages[i]
            VCSignal.Currents[i] = self.I_from_VR1R2R3(v,self.R1,self.R2,self.R3)
                       
    # ток через нашу упрощенную цепь - подробности см. в проекте vs_spice_solver
    def I_from_VR1R2R3(self,V,R1,R2,R3):
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







        

