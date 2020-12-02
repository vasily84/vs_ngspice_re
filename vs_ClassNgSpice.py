import numpy as np
import logging
from vs_utils import uuid_str
import subprocess
import vs_globals as G


class ClassNgSpice():
    def run_simulation(self):
        run_string = 'ngspice.exe -o nglog.txt -r out.raw -b -a -i {}'.format(self.fileName) 
        print(run_string)
        return subprocess.call(run_string)

    def save_model_file(self):
        # пишем заглушку
        with open(self.fileName, 'w') as newF:          
            newF.write('.title dual rc ladder\n')
            newF.write('R1 int in 10k\n')
            newF.write('V1 in 0 dc 0 PULSE (0 5 1u 1u 1u 1 1)\n')
            newF.write('R2 out int 1k\n')
            newF.write('C1 int 0 1u\n')
            newF.write('C2 out 0 100n\n')
            newF.write('.control\n')
            newF.write('save all\n')
            newF.write('run\n')
            newF.write('.endc\n')
            newF.write('.end\n')

    def __init__(self):
        self.fileName = uuid_str()+".cir"
