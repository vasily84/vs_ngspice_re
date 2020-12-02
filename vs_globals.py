import numpy as np

ngspice_dir = "ngspice_dir"
model_dir = "model_dir"

work_dir = model_dir

signal_Voltage = 2.5
signal_wfreq = 2.*np.pi*1e-3
signal_POINT_COUNT = 100
signal_dt = 1./(signal_POINT_COUNT*signal_wfreq)
