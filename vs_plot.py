import matplotlib.pyplot as plt
import numpy as np
import subprocess,os,glob
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
        plt.grid()
        plt.show()

        plt.draw() # перерисовка, обновление
        plt.gcf().canvas.flush_events()  
        if self.movieFileName is not None:
            fname = "framefile_%08d.png" % self.frameCount
            plt.savefig(fname)
            self.pngFiles.append(fname)
        self.frameCount+=1

    def begin(self,movieFileName=None):
        self.movieFileName = movieFileName
        self.frameCount = 0
        self.pngFiles = []
        plt.ion()
        plt.figure(1, (10, 5))
        plt.grid()
        
    def end(self):
        plt.ioff()
        if self.movieFileName is not None:
            if os.path.isfile(self.movieFileName):
                os.remove(self.movieFileName)

            subprocess.call([
            'ffmpeg', '-framerate', '8', '-i', 'framefile_%08d.png', '-r', '30', '-pix_fmt', 'yuv420p',
            self.movieFileName])
            for file_name in self.pngFiles: #glob.glob("*.png"):
                os.remove(file_name)
            #plt.show()
                