# проект vs_ngspice_re
# автор В. Симонов vasily_simonov@mail.ru github.com/vasily84
# язык Python, исследовательский проект

import numpy as np
import os
import vs_globals as G

def init():
    print(os.getcwd())
    os.chdir(G.work_dir)
    print(os.getcwd())
    

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