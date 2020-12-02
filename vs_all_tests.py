import unittest
import numpy as np

import vs_electronics_main
import vs_ClassObject
import vs_ClassModel
import vs_Signal
import os
import vs_globals as G
from vs_utils import uuid_str

class test_ClassObject(unittest.TestCase):
    def setUp(self):
        self.cb = vs_ClassObject.ClassObject()

    def NOtest_run_simulation(self):
        self.cb.save_model_file()
        runResult = self.cb.run_simulation()
        os.remove(self.cb.fileName)
        self.assertTrue(runResult==0)

    def NOtest_write_file(self):
        listDir1 = os.listdir('.')
        self.cb.save_model_file()
        listDir2 = os.listdir('.')
        cmpDir = len(listDir1)<len(listDir2)
        os.remove(self.cb.fileName)
        self.assertTrue(cmpDir)

class test_ClassModel_R(unittest.TestCase):
    def setUp(self):
        self.A = vs_ClassModel.ClassModel_R()

    def test_write_file(self):
        listDir1 = os.listdir('.')
        self.A.save_model_file()
        listDir2 = os.listdir('.')
        cmpDir = len(listDir1)<len(listDir2)
        os.remove(self.A.fileName)
        self.assertTrue(cmpDir)

    def test_saveAndLoad(self):
        B = vs_ClassModel.ClassModel_R()
        r1 = np.random.random()
        B.R = r1
        B.save_model_file()
        B.R = np.random.random()
        equ_false1 = B.R==r1
        B.load_model_from_file()
        equ_true1 = B.R==r1   
        os.remove(B.fileName)
        self.assertTrue(equ_false1==False and equ_true1==True)


    

class test_ModelSignal(unittest.TestCase):
    def setUp(self):
        pass

    def test_saveAndLoad(self):
        fileName = uuid_str()+'.npz'
        B = vs_Signal.ModelSignal()
        C = vs_Signal.ModelSignal()
        B.Voltages = B.Voltages*np.random.random()
        B.Currents = 1.*np.random.random()
        C.Voltages = C.Voltages*np.random.random()
        C.Currents = 1.*np.random.random()
        
        equ_false1 = np.array_equal(C.Voltages,B.Voltages)
        equ_false2 = np.array_equal(C.Currents,B.Currents)
        B.save(fileName)
        C.load(fileName)
        equ_true1 = np.array_equal(C.Voltages,B.Voltages)
        equ_true2 = np.array_equal(C.Currents,B.Currents)
        os.remove(fileName)
        self.assertTrue(equ_false1==False and equ_false2==False and equ_true1==True and equ_true2==True)


if __name__=='__main__':
    vs_electronics_main.init()
    unittest.main()
    vs_electronics_main.release()