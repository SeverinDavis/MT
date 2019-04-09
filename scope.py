import time
import visa
import numpy as np
from struct import unpack


def setup(scope, data, data_start, data_stop):
	scope.write('*RST')
	time.sleep(2)
	scope.write("TRIGger:A:EDGE:SOUrce CH1")
	scope.write('TRIGger:A:TYPe EDGE')
	scope.write('TRIGger:A:EDGE:COUPling DC')
	scope.write('TRIGger:A:EDGE:SLOpe EITHER')
	scope.write('TRIGger:A:HOLDoff:TIME 150E-03')
	#probe has as attenuation of 10 so 5V = 0.5 and 2.5V (Threshold) = 0.25
	scope.write('TRIGger:A:LEVel:CH1 0.25')
	scope.write('TRIGger:A:MODe NORMAL')
	scope.write('CH1:SCAle 200E-03')
	scope.write('CH2:SCAle 200E-03')
	scope.write('SELECT:CH1 1')
	scope.write('SELECT:CH2 1')
	#scope.write('ACQuire:MODe HIRES')
	scope.write('HORizontal:RECOrdlength ' + str(data))
	scope.write('DATA:START ' + str(data_start))
	scope.write('DATA:STOP ' + str(data_stop))



def capture(scope):
	#CHANNEL 1 DATA
	#select data output channel
	scope.write('DATA:SOU CH1')
	#1 byte per data point
	scope.write('DATA:WIDTH 1')
	scope.write('DATA:ENC RPB')
	ymult1 = float(scope.query('WFMPRE:YMULT?'))
	yzero1 = float(scope.query('WFMPRE:YZERO?'))
	yoff1 = float(scope.query('WFMPRE:YOFF?'))
	xincr1 = float(scope.query('WFMPRE:XINCR?'))
	scope.write('CURVE?')
	data1 = scope.read_raw()
	headerlen1 = 2 + int(data1[1])
	header1 = data1[:headerlen1]
	ADC_wave1 = data1[headerlen1:-1]
	ADC_wave1 = np.array(unpack('%sB' % len(ADC_wave1),ADC_wave1))
	Volts1 = (ADC_wave1 - yoff1) * ymult1  + yzero1
	Time1 = np.arange(0, xincr1 * len(Volts1), xincr1)

	#CHANNEL 2 DATA
	scope.write('DATA:SOU CH2')
	scope.write('DATA:WIDTH 1')
	scope.write('DATA:ENC RPB')
	ymult2 = float(scope.query('WFMPRE:YMULT?'))
	yzero2 = float(scope.query('WFMPRE:YZERO?'))
	yoff2 = float(scope.query('WFMPRE:YOFF?'))
	xincr2 = float(scope.query('WFMPRE:XINCR?'))
	scope.write('CURVE?')
	data2 = scope.read_raw()
	headerlen2 = 2 + int(data2[1])
	header2 = data2[:headerlen2]
	ADC_wave2 = data2[headerlen2:-1]
	ADC_wave2 = np.array(unpack('%sB' % len(ADC_wave2),ADC_wave2))
	Volts2 = (ADC_wave2 - yoff2) * ymult2  + yzero2
	Time2 = np.arange(0, xincr2 * len(Volts2), xincr2)

	return Time1, Volts1, Time2, Volts2