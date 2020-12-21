import os
import csv
import vs_Signal,vs_ClassModel
import vs_globals as G

"""
формирует единый датасет из вычислений для дальнейшего обучения нейросети.
"""
class vs_dataset:
    def writerow(self,row):
        with open(self.fileName,'a',newline='') as f:
            w = csv.writer(f,delimiter=';')
            w.writerow(row)

    def __init__(self,fileName=None):
        if fileName is None:
            self.fileName = 'VCsignals_dataset.csv'
        else:
            self.fileName = fileName

        if not os.path.isfile(self.fileName):
            title = ['recname','cmax','cmin','csumm','csumm2']
            for i in range(5):
                title.append('ampl_{}'.format(i)) 
                title.append('angle_{}'.format(i))

            title.append('kind')
            title.append('loss L2')
            title.append('loss L1')
            self.writerow(title)

    
    def lookForNearestSignal(self,targetSignal,epsilon=0.,maxcount=None):
        """ просканировать записи на предмет поиска наиболее 
        похожего сигнала """
        allFiles = os.listdir()
        signalFiles = [i for i in allFiles if i.endswith('.npz')]
        if maxcount is not None:
            if len(signalFiles)>maxcount:
                signalFiles = signalFiles[:maxcount]

        minFile = signalFiles[0]
        minVal = self.signalFile_scalar_cmp(minFile,targetSignal) 
        
        for sfile in signalFiles:
            v = self.signalFile_scalar_cmp(sfile,targetSignal)
            print(sfile+" "+str(v))
            if v<minVal:
                minVal = v
                minFile = sfile
            if v<=epsilon:
                break
        
        return minFile,minVal


    def signalFile_scalar_cmp(self,signalFileName,targetSignal):
        """ вернуть сравнение сигнала из файла с целевым сигналом targetSignal"""
        fileSignal = vs_Signal.ModelSignal()
        fileSignal.load(signalFileName)
        return fileSignal.scalar_cmp(targetSignal)


