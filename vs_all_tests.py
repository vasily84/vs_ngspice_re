import unittest
import numpy as np

import vs_electronics_main
import vs_ClassObject
import vs_ClassModel
import vs_Signal
import os
import vs_globals as G
from vs_utils import uuid_str,myplot
import vs_plot

# pylint: disable=E1101 # игнор линтинга numpy

@unittest.skip("Skip test_ClassObject")
class test_ClassObject(unittest.TestCase):
    def setUp(self):
        self.cb = vs_ClassObject.ClassObject()

    def test_run_simulation(self):
        self.cb.save_model_file()
        runResult = self.cb.run_simulation()
        os.remove(self.cb.fileName)
        self.assertTrue(runResult==0)

    def test_write_file(self):
        listDir1 = os.listdir('.')
        self.cb.save_model_file()
        listDir2 = os.listdir('.')
        cmpDir = len(listDir1)<len(listDir2)
        os.remove(self.cb.fileName)
        self.assertTrue(cmpDir)


#@unittest.skip("Skip test_ClassModel_R")
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
        B.R1 = r1
        B.save_model_file()
        B.R1 = np.random.random()
        equ_false1 = (B.R1==r1)
        B.load_model_from_file()
        equ_true1 = (B.R1==r1)   
        os.remove(B.fileName)
        self.assertTrue((not equ_false1) and equ_true1)

#@unittest.skip("Skip test_Rphase")
class test_ClassModel_Rphase(unittest.TestCase):
    def test_scalar_optimization_Rphase(self):
        modelA = vs_ClassModel.ClassModel_Rphase(10,1)
        targetModel = vs_ClassModel.ClassModel_Rphase(130,10)

        G.targetSignal = vs_Signal.ModelSignal('target')
        targetModel.run_simulation(G.targetSignal)
        G.modelSignal = vs_Signal.ModelSignal('model')
        G.modelSignal.copy(G.targetSignal)
        G.modelSignal.Currents[:] = 0
        xres = modelA.run_scalar_optimization()
        self.assertTrue(xres.success)

    @unittest.skip("")
    def test_phaseShift(self):
        targetModel = vs_ClassModel.ClassModel_Rphase(1.,10)
        G.targetSignal = vs_Signal.ModelSignal('target')
        targetModel.run_simulation(G.targetSignal)
        myplot(G.targetSignal,G.modelSignal)
        myplot((G.targetSignal.Voltages),(G.targetSignal.Currents))
        self.assertTrue(True)
        

#@unittest.skip("Skip test_ModelSignal")
class test_ModelSignal(unittest.TestCase):
    def test_scalar_optimization_R1R2R3(self):
        modelA = vs_ClassModel.ClassModel_R1R2R3()
        targetModel = vs_ClassModel.ClassModel_R1R2R3()

        G.targetSignal = vs_Signal.ModelSignal('target')
        #targetModel = vs_ClassModel.ClassModel_DR()
        r1 = G.small_R+np.random.random()*1e3
        r2 = G.small_R+np.random.random()*1e3
        r3 = G.small_R+np.random.random()*1e3
        targetModel.setXi([r1,r2,r3])
        targetModel.run_simulation(G.targetSignal)
        G.modelSignal = vs_Signal.ModelSignal('model')
        G.modelSignal.copy(G.targetSignal)
        G.modelSignal.Currents[:] = 0
        xres = modelA.run_scalar_optimization()
        self.assertTrue(xres.success)

    def child_scalar_optimization_1d(self,modelA,targetModel):
        G.targetSignal = vs_Signal.ModelSignal('target')
        targetModel.setXi([G.small_R+np.random.random()*1e3])
        targetModel.run_simulation(G.targetSignal)
        G.modelSignal = vs_Signal.ModelSignal('model')
        G.modelSignal.copy(G.targetSignal)
        G.modelSignal.Currents[:] = 0
        xres = modelA.run_scalar_optimization()
        return xres

    def test_scalar_optimization_R(self):
        A = vs_ClassModel.ClassModel_R()
        target = vs_ClassModel.ClassModel_R()
        xres = self.child_scalar_optimization_1d(A,target)
        self.assertTrue(xres.success)

    def test_scalar_optimization_RD(self):
        A = vs_ClassModel.ClassModel_DR()
        target = vs_ClassModel.ClassModel_DR()
        xres = self.child_scalar_optimization_1d(A,target)
        self.assertTrue(xres.success)

    def test_scalar_optimization_DR(self):
        A = vs_ClassModel.ClassModel_DR()
        target = vs_ClassModel.ClassModel_DR()
        xres = self.child_scalar_optimization_1d(A,target)
        self.assertTrue(xres.success)

    def test_saveAndLoad(self):
        fileName = uuid_str()+'.npz'
        B = vs_Signal.ModelSignal()
        C = vs_Signal.ModelSignal()
        B.Voltages = B.Voltages*np.random.random()
        B.Currents[:] = 1.*np.random.random()
        C.Voltages = C.Voltages*np.random.random()
        C.Currents[:] = 1.*np.random.random()
        
        equ_false1 = np.array_equal(C.Voltages,B.Voltages)
        equ_false2 = np.array_equal(C.Currents,B.Currents)
        B.save(fileName)
        C.load(fileName)
        equ_true1 = np.array_equal(C.Voltages,B.Voltages)
        equ_true2 = np.array_equal(C.Currents,B.Currents)
        os.remove(fileName)
        self.assertTrue((not equ_false1) and (not equ_false2) and equ_true1 and equ_true2)

@unittest.skip("Skip test_ModelSignal")
class test_CInteractivePlot(unittest.TestCase):
    def test_1(self):
        B = vs_Signal.ModelSignal()
        C = vs_Signal.ModelSignal()
        B.Voltages = B.Voltages*np.random.random()
        B.Currents[:] = 1.*np.random.random()
        C.Voltages = C.Voltages*np.random.random()
        C.Currents[:] = 1.*np.random.random()
        out = vs_plot.InteractivePlot()
        out.begin()
        for _ in range(10):
            B.Voltages = B.Voltages*np.random.random()
            B.Currents[:] = 1.*np.random.random()
            C.Voltages = C.Voltages*np.random.random()
            C.Currents[:] = 1.*np.random.random()
            out.plot(B,C)
            
        out.end()

        self.assertTrue(True)

if __name__=='__main__':
    vs_electronics_main.init()
    unittest.main()
    vs_electronics_main.release()