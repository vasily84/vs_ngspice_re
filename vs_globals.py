import numpy as np

ngspice_dir = "ngspice_dir"
model_dir = "model_dir"

work_dir = model_dir

signal_Voltage = 2.5
signal_POINT_COUNT = 360
signal_dt = 1e-5
signal_CurrentNoiseAmplitude = 0.

targetSignal = None
modelSignal = None

DIODE_VOLTAGE = 0.6
small_R = 1e-6
