'''
    Serial Port Reader:
    un semplice script per leggere e stampare a video
    i dati emessi da un dispositivo seriale.
'''
import os
import threading
import queue
import time
import serial
import signal
import sys
import subprocess

DEVICE_NAME = ["Kendau GPS", "Control Unit", "Gyroscope"]
SERIAL_PORT = ["/dev/mypty/ptySENS1_V", "/dev/mypty/ptySENS2_V", "/dev/mypty/ptySENS3_V"]
BAUDRATE = 9600
FINISH_CHK_LOOP = 3
shutdown = False
socat_script_path = "./socat.sh"

buffer = queue.Queue()  # semplice queue FIFO

class serial_port:
	def __init__(self,label,port_number,baudrate):
		self.label = label
		self.port = serial.Serial()
		self.port.port = port_number
		self.port.baudrate = baudrate
		self.open = False
		self.port.bytesize = serial.EIGHTBITS
		self.port.parity = serial.PARITY_NONE
		self.port.stopbits = serial.STOPBITS_ONE
		self.port.timeout = 20         	# Leggeremo una linea per volta: il timeout (in secondi) serve a non rimanere bloccati in caso di assenza di dati dal dispositivo
		self.port.xonxoff = False    	# disabilita il flusso di controllo software
		self.port.rtscts = False     	# disabilita il flusso di controllo hardware (RTS/CTS)
		self.port.dsrdtr = False     	# disabilita il flusso di controllo hardware (DSR/DTR)

	def open_connection(self):
		if not self.open:
			print('('+self.label+') opening connection')
			self.port.open()
			self.open = True

	def read_line(self):
		try:
			line = str(self.port.readline().decode('ascii')).strip()
		except:
			line = ''
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

def serial_port_handler(dev_name, port, baudrate):
	
	print(f"Running handler for port {port}...")
	s_port = serial_port(dev_name, port, baudrate)
	s_port.open_connection()

	while not shutdown:
		line = s_port.read_line()
		if len(line) > 0:
			buffer.put(line)
	
	print(f"Closing handler for port {port}...")
	s_port.close_connection()

if __name__ == '__main__':

	# Creates 3 serial ports couples with socat
	# GPS data is transmitted on 			/dev/mypty/ptySENS1 and read on /dev/mypty/ptySENS1_V
	# Control Unit data is transmitted on 	/dev/mypty/ptySENS2 and read on /dev/mypty/ptySENS2_V
	# Gyroscope data is transmitted on 		/dev/mypty/ptySENS3 and read on /dev/mypty/ptySENS3_V
	socat_process = subprocess.Popen(socat_script_path)

	for item in SERIAL_PORT:
		print(f"Listening for messages on {item}.")

	time.sleep(2)

	# 3 serial ports receiving data
	signal.signal(signal.SIGINT, signal_handler)
	print('Press Ctrl+C to stop and exit!')


	thread_1 = threading.Thread(target=serial_port_handler, args=[DEVICE_NAME[0], SERIAL_PORT[0], BAUDRATE])
	thread_2 = threading.Thread(target=serial_port_handler, args=[DEVICE_NAME[1], SERIAL_PORT[1], BAUDRATE])
	thread_3 = threading.Thread(target=serial_port_handler, args=[DEVICE_NAME[2], SERIAL_PORT[2], BAUDRATE])

	thread_1.start()
	thread_2.start()
	thread_3.start()

	while not shutdown:
		print(buffer.get())

	while thread_1.is_alive() or thread_2.is_alive() or thread_3.is_alive():
		time.sleep(FINISH_CHK_LOOP)

	socat_process.kill()
	sys.exit(0)
