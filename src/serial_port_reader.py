from threading import Thread
from queue import Queue, Empty
import multiprocessing 
import time
import serial
import subprocess
import signal
import os
import logging, logging.config
import serial.serialutil

DEVICE_NAME = ["Kendau GPS", "Control Unit", "Gyroscope"]
SERIAL_PORT = ["../mypty/ptySENS1_V", "../mypty/ptySENS2_V", "../mypty/ptySENS3_V"]
BAUDRATE = 9600
FINISH_CHK_LOOP = 3
serial_ports_path = "../mypty/"
socat_script_path = "./socat.sh"

def init_logger():
	global serial_logger
	logging.config.fileConfig('../logging.conf')
	serial_logger = logging.getLogger("serial_logger")

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
		self.port.timeout = 20
		self.port.xonxoff = False
		self.port.rtscts = False
		self.port.dsrdtr = False

	def open_connection(self):
		if not self.open:
			serial_logger.info('['+self.label+'] opening connection')
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
			serial_logger.info('['+self.label+'] closing connection')
			self.port.close()
			self.open = False

	def __del__(self):
		if self.open:
			self.port.close()
			self.open = False

def serial_port_handler(dev_name, port, baudrate, buffer: Queue):
	s_port = serial_port(dev_name, port, baudrate)
	try:
		s_port.open_connection()
		while not shutdown:
			line = s_port.read_line()
			if len(line) > 0:
				buffer.put(line)
	except serial.serialutil.SerialException:
		raise serial.serialutil.SerialException
	
	# print(f"Closing handler for port {port}...")
	s_port.close_connection()

def run_serial_port_handler(index) -> tuple[Thread, Queue]:
	buffer = Queue()  # semplice queue FIFO

	try: 
		thread = Thread(target=serial_port_handler, args=[DEVICE_NAME[index], SERIAL_PORT[index], BAUDRATE, buffer])
	except:
		serial_logger.error("Something went wrong while initializing port handler.")
		raise serial.serialutil.SerialException
		
	thread.start()
	return (thread, buffer)

def signal_handler(signal, frame):
	global shutdown
	shutdown = True

# p are the 3 message channels to data_parser
# p1 = Kendau GPS
# p2 = Control Unit
# p3 = Gyroscope

def start_serial_port_reader(p: list[multiprocessing.Queue]):
	# Creates 3 serial ports couples with socat
	# GPS data is transmitted on 			/dev/mypty/ptySENS1 and read on /dev/mypty/ptySENS1_V
	# Control Unit data is transmitted on 	/dev/mypty/ptySENS2 and read on /dev/mypty/ptySENS2_V
	# Gyroscope data is transmitted on 		/dev/mypty/ptySENS3 and read on /dev/mypty/ptySENS3_V

	init_logger()

	global shutdown
	shutdown = False

	signal.signal(signal.SIGINT, signal_handler)
	
	if not os.path.exists(serial_ports_path):
		os.mkdir(serial_ports_path)

	socat_process = subprocess.Popen(socat_script_path)

	for item in SERIAL_PORT:
		serial_logger.info(f"Listening for messages on {item}.")

	time.sleep(2)
	buffers: list[Queue] = []
	threads: list[Thread] = []

	for i in range(3):
		try:
			(thrd, buff) = run_serial_port_handler(i)
			buffers.append(buff)
			threads.append(thrd)
		except serial.serialutil.SerialException:
			shutdown = True

	# loops over buffers, checks one per time if there is anything to print
	while not shutdown:
		
		empty_counter = 0

		for i in range(3):
			try:
				msg = buffers[i].get(False)
				# Sends data from the buffer to data_parser
				p[i].put(msg)
			except Empty:
				# print("Buffer is empty")
				empty_counter += 1
		
		# Wait 1 sec all the pipes are empty
		if empty_counter == 3:
			time.sleep(2)

	# waits that all the threads finished (if the signal_handler is alted)
	while threads[0].is_alive() or threads[1].is_alive() or threads[2].is_alive():
		time.sleep(FINISH_CHK_LOOP)
	
	# If there is data in the queue, this is required to unjoin the thread
	for pipe in p:
		pipe.cancel_join_thread()
		pipe.close()

	
	socat_process.kill()

	serial_logger.warning("Cleaning serial ports directory.")
	clean_serial_path()

	serial_logger.info("Closing Serial Reader")

def clean_serial_path():
	try:
		os.removedirs(serial_ports_path)
	except OSError:
		for item in os.listdir(serial_ports_path):
			os.remove(f"../mypty/{item}")
		os.removedirs(serial_ports_path)

if __name__ == "__main__":
	w_pipe = multiprocessing.Queue()
	w2_pipe = multiprocessing.Queue()
	w3_pipe = multiprocessing.Queue()

	p: list[multiprocessing.Queue] = [w_pipe, w2_pipe, w3_pipe]

	start_serial_port_reader(p)
