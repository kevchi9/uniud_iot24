from threading import Thread
from queue import Queue, Empty
import time
import serial
import subprocess
import signal
from multiprocessing import Pipe

shutdown = False

DEVICE_NAME = ["Kendau GPS", "Control Unit", "Gyroscope"]
SERIAL_PORT = ["/dev/mypty/ptySENS1_V", "/dev/mypty/ptySENS2_V", "/dev/mypty/ptySENS3_V"]
BAUDRATE = 9600
FINISH_CHK_LOOP = 3
socat_script_path = "./socat.sh"

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

def serial_port_handler(dev_name, port, baudrate, buffer: Queue):
	
	print(f"Starting handler for port {port}...")
	s_port = serial_port(dev_name, port, baudrate)
	s_port.open_connection()

	while not shutdown:
		line = s_port.read_line()
		if len(line) > 0:
			buffer.put(line)
	
	print(f"Closing handler for port {port}...")
	s_port.close_connection()

def run_serial_port_handler(index) -> tuple[Thread, Queue]:
	buffer = Queue()  # semplice queue FIFO
	thread = Thread(target=serial_port_handler, args=[DEVICE_NAME[index], SERIAL_PORT[index], BAUDRATE, buffer])
	thread.start()
	return (thread, buffer)

# Pipe is the message channel to data_parser
def start_serial_port_reader(pipe):
	# Creates 3 serial ports couples with socat
	# GPS data is transmitted on 			/dev/mypty/ptySENS1 and read on /dev/mypty/ptySENS1_V
	# Control Unit data is transmitted on 	/dev/mypty/ptySENS2 and read on /dev/mypty/ptySENS2_V
	# Gyroscope data is transmitted on 		/dev/mypty/ptySENS3 and read on /dev/mypty/ptySENS3_V

	signal.signal(signal.SIGINT, signal_handler)
	print('Press Ctrl+C to stop and exit!')

	socat_process = subprocess.Popen(socat_script_path)

	for item in SERIAL_PORT:
		print(f"Listening for messages on {item}.")

	time.sleep(2)
	
	buffers: list[Queue] = []
	threads: list[Thread] = []

	for i in range(3):
		(thrd, buff) = run_serial_port_handler(i)
		buffers.append(buff)
		threads.append(thrd)

	# loops over buffers, checks one per time if there is anything to print
	while not shutdown:

		# TODO: it iterates over buffers and a lot of time is wasted, find a way to optimize this
		for buffer in buffers:
			try:
				msg = buffer.get(False)
				# Sends data from the buffer to data_parser
				# TODO: manage the 3 buffers in 3 separated channels
				pipe.send(msg)
			except Empty:
				# print("Buffer is empty")
				continue
			except:
				print("An error occurred while getting data from buffer.")

	# waits that all the threads finished (if the signal_handler is alted)
	while threads[0].is_alive() or threads[1].is_alive() or threads[2].is_alive():
		time.sleep(FINISH_CHK_LOOP)

	pipe.close()
	socat_process.kill()
