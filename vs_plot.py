import matplotlib.pyplot as plt
import numpy as np
import vs_Signal


class InteractivePlot():
    def plot(self,*args):
        plt.clf()

        # Отобразить график
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

        plt.draw() # перерисовка, обновление
        plt.gcf().canvas.flush_events()


    def begin(self):
        plt.ion()
        
    def end(self):
        plt.ioff()
        #plt.show()
            
