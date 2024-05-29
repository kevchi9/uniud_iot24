from time import sleep
import signal
from multiprocessing import Process, Pipe
from serial_port_reader import start_serial_port_reader
from data_parser import start_data_parser
from data_publisher import start_data_publisher

shutdown = False

def signal_handler(signal, frame):
	global shutdown
	shutdown = True
	print('You pressed Ctrl+C!\nExiting...')

def main():

    # Pipes used for inter-process communication
    (w_pipe, r_pipe) = Pipe()
    (w2_pipe, r2_pipe) = Pipe()

    # Signal is sent also to all child processes
    signal.signal(signal.SIGINT, signal_handler)

    Process(target=start_serial_port_reader, name="serial_port_reader.py", args=(w_pipe, )).start()
    Process(target=start_data_parser, name="data_parser.py", args=(r_pipe, w2_pipe, )).start()
    Process(target=start_data_publisher, name="data_publisher.py", args=(r2_pipe, )).start()

    while not shutdown:
        sleep(3)

if __name__ == "__main__":
    main()
