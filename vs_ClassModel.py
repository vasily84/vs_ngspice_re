import numpy as np
from vs_utils import uuid_str
import vs_globals as G
import vs_Signal
import json


class ClassModel():
    def run_simulation(self,inputSignal):
        self.save_model_file()
        self.evaluate_model(inputSignal)
        inputSignal.save(self.signalFileName)
        return 0

    def run_scalar_optimization(self,targetSignal):
        pass

    def optimization_subroutine(self,Xi):
        pass 
    
    def newFileName(self):
        coreName = uuid_str()
        self.fileName = coreName+".m_json"
        self.signalFileName = coreName+".npz"

    def __init__(self):
        self.newFileName()



class ClassModel_R(ClassModel):
    def __init__(self, R=100):
        super().__init__()
        self.R = R

    def save_model_file(self):
        json_list = {"model_type":"R","R":self.R}
        with open(self.fileName, 'w') as newFile:   
            json.dump(json_list,newFile)   

    def load_model_from_file(self):   
        with open(self.fileName, "r") as read_file:
            jsonModel = json.load(read_file) 
        self.R = jsonModel["R"]
        
    def evaluate_model(self,Signal):
        Signal.Currents = Signal.Voltages/self.R

    def init_starts_from_signal(self,VCSignal):
        """найтии НУ для схемы исходя из сигнала"""
        self.R = 200 #!!





        

