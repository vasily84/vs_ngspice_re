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
            self.writerow(title)

