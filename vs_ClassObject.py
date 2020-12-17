#
import numpy as np
import scipy.optimize as spo
import json

from vs_utils import uuid_str
import vs_globals as G
import vs_Signal
import vs_plot   
      
# pylint: disable=E1101 # игнор линтинга виртуальных методов

class ClassObject():
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



