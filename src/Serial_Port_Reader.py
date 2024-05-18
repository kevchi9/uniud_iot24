'''
    Serial Port Reader:
      un semplice script per leggere e stampare a video
        i dati emessi da un dispositivo seriale.
'''
import serial
import signal
import sys

DEVICE_NAME="Kendau GPS"
SERIAL_PORT="/dev/pts/3"
BAUDRATE=9600
shutdown = False

class serial_port:
	def __init__(self,label,port_number,baudrate):
		self.label = label
		self.port = serial.Serial()
		self.port.port = port_number
		self.port.baudrate=baudrate
		self.open=False
		self.port.bytesize=serial.EIGHTBITS
		self.port.parity=serial.PARITY_NONE
		self.port.stopbits=serial.STOPBITS_ONE
		self.port.timeout=20         # Leggeremo una linea per volta: il timeout (in secondi) serve a non rimanere bloccati in caso di assenza di dati dal dispositivo
		self.port.xonxoff = False    # disabilita il flusso di controllo software
		self.port.rtscts = False     # disabilita il flusso di controllo hardware (RTS/CTS)
		self.port.dsrdtr = False     # disabilita il flusso di controllo hardware (DSR/DTR)

	def open_connection(self):
		if not self.open:
			print('('+self.label+') opening connection')
			self.port.open()
			self.open = True

	def read_line(self):
		try:
			line = str(self.port.readline().decode('ascii')).strip()
		except:
			line=''
		return line

	def close_connection(self):
		if self.open:
			print('('+self.label+') closing connection')
			self.port.close()
			self.open = False

	def __del__(self):
		if self.open:
			self.port.close()
			self.open = False

def signal_handler(signal, frame):
	global shutdown
	shutdown = True
	print('You pressed Ctrl+C!\nExiting...')

s_port=serial_port(DEVICE_NAME,SERIAL_PORT,BAUDRATE)

signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C to stop and exit!')

s_port.open_connection()

while not shutdown:
	line=s_port.read_line()
	if len(line)>0:
		print(line)

s_port.close_connection()
sys.exit(0)
