from uuid import uuid4
import numpy as np
import matplotlib.pyplot as plt
import vs_Signal

def uuid_str():
    return uuid4().hex

    
def myplot(*args):
    plt.figure(1, (20, 10))
    plt.grid()
    if isinstance(args[0],vs_Signal.ModelSignal):
        plt.ylabel('Current, [A]')
        plt.xlabel('Voltage, [V]')
        for s in args:
            plt.plot(s.Voltages,s.Currents,label=s.Title)

    elif isinstance(args[0],np.ndarray):
        for s in args:
            plt.plot(s)

    plt.legend(loc='best')
    plt.show()

def begin_plot():
    pass

def end_plot():
    pass

def update_plot():
    pass

    


