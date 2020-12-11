# проект vs_ngspice_re
# автор В. Симонов vasily_simonov@mail.ru github.com/vasily84
# язык Python, исследовательский проект

import numpy as np
import os
import vs_globals as G
import vs_Signal
import vs_ClassModel
from vs_utils import myplot
import vs_dataset

def init():
    if os.path.isdir(G.work_dir)==False:
        os.mkdir(G.work_dir)
    os.chdir(G.work_dir)
    G.dataset = vs_dataset.vs_dataset()
    
    G.targetSignal = vs_Signal.ModelSignal('target')
    targetModel = vs_ClassModel.ClassModel_R()
    targetModel.R1 = 333.
    targetModel.run_simulation(G.targetSignal)
    G.modelSignal = vs_Signal.ModelSignal('model')
    G.modelSignal.copy(G.targetSignal)
    G.modelSignal.Currents[:] = 0

def do_job():
    pass
    

def release():
    pass

def main():
    init()
    do_job()
    release()

if __name__=='__main__':
    main()