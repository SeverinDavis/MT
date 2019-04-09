#-------------------------------------------------------------------------------
#  Get a screen catpure from DPO4000 series scope and save it to a file

# python        2.7         (http://www.python.org/)
# pyvisa        1.4         (http://pyvisa.sourceforge.net/)
# numpy         1.6.2       (http://numpy.scipy.org/)
# MatPlotLib    1.0.1       (http://matplotlib.sourceforge.net/)
#-------------------------------------------------------------------------------

import visa
import numpy as np
from struct import unpack
import pylab
import time
import csv
import serial
import scope as osc
import status

port = ""
osilloscope = "" 
directory_open = ""
directory_close = ""
post_sample = 1
iterations = 0
delay = 0

module = "NAME"
iteration_start = 0
iteration_counter = 0

iteration_sample = 1

minutes = -1



oscilloscope_sample = str(10000000)
oscilloscope_sample_start = str(4990000)
oscilloscope_sample_stop = str(5700000)

temperature_threshold = 0

def main():

	timed = False
	noosc = False


	with open('config.txt') as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		line_count = 0
		for row in csv_reader:
			key = row[0]
			value = row[1]
			print(str(row[0]))
			print(str(row[1]))
			line_count += 1
			if(key == "port"):
				port = value
			elif(key == "oscilloscope"):
				oscilloscope = value
			elif(key == "directory_open"):
				directory_open = value
			elif(key == "directory_close"):
				directory_close = value
			elif(key == "post_sample"):
				post_sample = int(value)
			elif(key == "iterations"):
				iterations = int(value)
			elif(key == "oscilloscope_sample"):
				oscilloscope_sample = value
			elif(key == "oscilloscope_sample_start"):
				oscilloscope_sample_start = value
			elif(key == "oscilloscope_sample_stop"):
				oscilloscope_sample_stop = value
			elif(key == "temperature_threshold"):
				temperature_threshold = (int(value)).to_bytes(1, byteorder="big")
			elif(key == "gas_threshold"):
				gas_threshold = (int(value)).to_bytes(1, byteorder="big")
			elif(key == "voltage_threshold"):
				voltage_threshold = (int(value)).to_bytes(1, byteorder="big")
			elif(key == "module"):
				module = value
			elif(key == "iteration_start"):
				iteration_start = int(value)
				iteration_counter = iteration_start
			elif(key =="minutes"):
				minutes = int(value)
				timed = True
			elif(key == "noosc"):
				noosc = True
			elif(key == "iteration_sample"):
				iteration_sample = int(value)
			elif(key == "delay"):
				delay = float(value)
			elif(key == "sample_delay"):
				sample_delay = (int(value)).to_bytes(1, byteorder="big")


		print(f'Read {line_count} lines.')

	rm = visa.ResourceManager()
	scope = rm.get_instrument(oscilloscope)
	ser = serial.Serial(port, 9600, timeout=1, dsrdtr=False, rtscts=False)
	print(ser.name)

	osc.setup(scope, oscilloscope_sample, oscilloscope_sample_start, oscilloscope_sample_stop)

	input("Press Enter to continue...")

	error = 0

#Confirm that module started up initilized in expected mode
	print("Confirming Config Mode")
	ser.write(b'\x80')
	ser.write(b'\x80')
	state = ser.read(1)
	state = int.from_bytes(state, byteorder='big')
	status.print_status(state)
	if(status.mode_is_timeout(state)):
		print('Exiting...')
		return
	if not status.mode_is_config(state):
		print("Module is in wrong mode")
		return
	print("Config Mode confirmed")

	print("");

	print("Setting Temperature Threshold")
	ser.write(bytes(b'\x21'))
	ser.write(temperature_threshold)
	state0 = ser.read(1)
	state1 = ser.read(1)
	state0 = int.from_bytes(state0, byteorder='big')
	state1 = int.from_bytes(state1, byteorder='big')
	status.print_status(state1)
	if(status.mode_is_timeout(state1)):
		print('Exiting...')
		return
	if not status.mode_is_config(state1):
		print("Module is in wrong mode")
		return
	print("Temperature set to: " + str(state0) + " or " + str(state0/2.0) + "degC")

	print("")

	print("Setting Gas Threshold")
	ser.write(bytes(b'\x22'))
	ser.write(gas_threshold)
	state0 = ser.read(1)
	state1 = ser.read(1)
	state0 = int.from_bytes(state0, byteorder='big')
	state1 = int.from_bytes(state1, byteorder='big')
	status.print_status(state1)
	if(status.mode_is_timeout(state1)):
		print('Exiting...')
		return
	if not status.mode_is_config(state1):
		print("Module is in wrong mode")
		return
	print("Gas set to: " + str(state0))

	print("")

	print("Setting Voltage Threshold")
	ser.write(bytes(b'\x24'))
	ser.write(voltage_threshold)
	state0 = ser.read(1)
	state1 = ser.read(1)
	state0 = int.from_bytes(state0, byteorder='big')
	state1 = int.from_bytes(state1, byteorder='big')
	status.print_status(state1)
	if(status.mode_is_timeout(state1)):
		print('Exiting...')
		return
	if not status.mode_is_config(state1):
		print("Module is in wrong mode")
		return
	print("Voltage set to: " + str(state0) + " or " + str(state0/2.0/100) + "volts")

	print("")

	print("Setting Sample Delay ")
	ser.write(bytes(b'\x30'))
	ser.write(sample_delay)
	state0 = ser.read(1)
	state1 = ser.read(1)
	state0 = int.from_bytes(state0, byteorder='big')
	state1 = int.from_bytes(state1, byteorder='big')
	status.print_status(state1)
	if(status.mode_is_timeout(state1)):
		print('Exiting...')
		return
	if not status.mode_is_config(state1):
		print("Module is in wrong mode")
		return
	print("Delay set to: " + str(state0) + "ms")


#Confirm that module switched to run mode
	print("Confirming Run Mode")
	ser.write(b'\x40')
	ser.write(b'\x40')
	state = ser.read(1)
	state = int.from_bytes(state, byteorder='big')
	status.print_status(state)
	if(status.mode_is_timeout(state)):
		print('Exiting...')
		return
	if not status.mode_is_run(state):
		print("Module is in wrong mode")
		return
	print("Run Mode confirmed")

	start_time = time.monotonic()
	end_time = start_time + minutes*60.0
	print(str(start_time))
	print(str(end_time))

	return
#perform the requested number of iterations
	while (iteration_counter < iterations and not timed) or (timed and time.monotonic()<end_time):
#instruct module to bring control signal high
#and wait for response
		print("")
		print()
		print("Iteration " + str(iteration_counter - iteration_start))
		print( str(round((end_time - time.monotonic())/60.0 , 2)) + " minutes remaining")
		print("Positive Edge")
		ser.write(b't')
		state = ""
		state = ser.read(1)
		state = int.from_bytes(state, byteorder='big')
		status.print_status(state)

#verify that returned state contains no errors
		if(status.mode_is_timeout(state)):
			print('Exiting...')
			return
		if(state & 0x3F != 0x00):
			print('Exiting...')
			return

#retrieve capture data
		if noosc:
			time.sleep(delay)


		if ((iteration_counter - iteration_start) % iteration_sample == 0):
			capture = osc.capture(scope)

			Volts1 = capture[1]
			Volts2 = capture[3]
			Time1 = capture[0]
			Volts1 = Volts1[::post_sample]
			Volts2 = Volts2[::post_sample]
			Time1 = Time1[::post_sample]

			timestr = time.strftime("%Y%m%d-%H%M%S")

			
			with open(directory_close + module + "_c_" + str(iteration_counter) + "_" + timestr + ".csv", mode='w', newline='') as osc_file:
			    osc_writer = csv.writer(osc_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			    for index, volt in enumerate(Volts1, start=0):   # default is zero
				    osc_writer.writerow([str(Time1[index]), str(volt), str(Volts2[index])])

		print("");
		print("Negative Edge")
		ser.write(b'y')
		state = ""
		state = ser.read(1)
		state = int.from_bytes(state, byteorder='big')
		status.print_status(state)

		if(status.mode_is_timeout(state)):
			print('Exiting...')
			return
		if(state & 0x3F != 0x00):
			print('Exiting...')
			capture = osc.capture(scope)

			Volts1 = capture[1]
			Volts2 = capture[3]
			Time1 = capture[0]
			Volts1 = Volts1[::post_sample]
			Volts2 = Volts2[::post_sample]
			Time1 = Time1[::post_sample]

			timestr = time.strftime("%Y%m%d-%H%M%S")

			with open(directory_open + module + "_o_" + str(iteration_counter) + "_" + timestr+".csv", mode='w', newline='') as osc_file:
			    osc_writer = csv.writer(osc_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			    for index, volt in enumerate(Volts1, start=0):   # default is zero
				    osc_writer.writerow([str(Time1[index]), str(volt), str(Volts2[index])])
			return

		if noosc:
			time.sleep(delay)

		if ((iteration_counter - iteration_start) % iteration_sample == 0):
			capture = osc.capture(scope)

			Volts1 = capture[1]
			Volts2 = capture[3]
			Time1 = capture[0]
			Volts1 = Volts1[::post_sample]
			Volts2 = Volts2[::post_sample]
			Time1 = Time1[::post_sample]

			timestr = time.strftime("%Y%m%d-%H%M%S")

			with open(directory_open + module + "_o_" + str(iteration_counter) + "_" + timestr+".csv", mode='w', newline='') as osc_file:
			    osc_writer = csv.writer(osc_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			    for index, volt in enumerate(Volts1, start=0):   # default is zero
				    osc_writer.writerow([str(Time1[index]), str(volt), str(Volts2[index])])

		iteration_counter = iteration_counter + 1

	print("")
	print("Completed " + str(iteration_counter - iteration_start) + " iterations")
	print("Entering Config Mode")
	print("Confirming Config Mode")
	ser.write(b'\x80')
	state = ser.read(1)
	state = int.from_bytes(state, byteorder='big')
	status.print_status(state)
	if(status.mode_is_timeout(state)):
		print('Exiting...')
		return
	if not status.mode_is_config(state):
		print("Module is in wrong mode")
		return
	print("Config Mode confirmed")

if __name__ == "__main__":
    main()


