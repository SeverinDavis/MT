TEMPERATURE = 0x01
GAS = 0x02
VOLTAGE = 0x04
DELAY = 0x10

TEST_SUCCESS = 0x3F

ERROR_RELAY_OPEN = 0x04
ERROR_RELAY_CLOSED = 0x08

MODE_CONFIG = 0x80
MODE_RUN = 0x40
MODE_ERROR = 0xC0
MODE_TIMEOUT = 0x00

WRITE = 0x20



def print_status(state):
	if(state&MODE_ERROR == MODE_ERROR):
		print("ERROR MODE")
	elif(state&MODE_ERROR == MODE_TIMEOUT):
		print("TIMEOUT")
	elif(state&MODE_ERROR == MODE_CONFIG):
		print("CONFIG MODE")
	elif(state&MODE_ERROR == MODE_RUN):
		print("RUN MODE")
	if(state&TEST_SUCCESS == 0x00):
		print("OK")
	if(state&WRITE):
		print("WRITE OPERATION:")
		if(state&TEMPERATURE):
			print("TEMPERATURE")
		if(state&GAS):
			print("GAS LEVEL")
		if(state&ERROR_RELAY_OPEN):
			print("VOLTAGE LEVEL")
		if(state&ERROR_RELAY_CLOSED):
			print("VOLTAGE LEVEL")	
		if(state&DELAY):
			print("DELAY")
	else:
		if(state&TEMPERATURE):
			print("TEMPERATURE EXCEEDED")
		if(state&GAS):
			print("GAS LEVEL EXCEEDED")
		if(state&ERROR_RELAY_OPEN):
			print("RELAY STUCK OPEN")
		if(state&ERROR_RELAY_CLOSED):
			print("RELAY STUCK CLOSED")	


def mode_is_run(state):
	return (state&MODE_ERROR == MODE_RUN)

def mode_is_config(state):
	return (state&MODE_ERROR == MODE_CONFIG)

def mode_is_timeout(state):
	return (state&MODE_ERROR == MODE_TIMEOUT)