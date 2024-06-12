from time import sleep
import signal
from multiprocessing import Process, Queue
from serial_port_reader import start_serial_port_reader
from data_parser import start_data_parser
from data_publisher import start_data_publisher
import logging, logging.config

shutdown = False

def signal_handler(signal, frame):
	global shutdown
	shutdown = True
	root_logger.info('You pressed Ctrl+C!')


def init_logger():
	global root_logger
	logging.config.fileConfig('../logging.conf')
	root_logger = logging.getLogger("main_logger")

# Generates 6 Queues
def get_pipes() -> tuple[Queue, Queue, Queue, Queue, Queue, Queue]:
    return (Queue(), Queue(), Queue(), Queue(), Queue(), Queue())

def main():
    
    init_logger()

    # Pipes used for inter-process communication
    (p1, p2, p3, p4, p5, p6) = get_pipes()    
    p_to_parser = [p1, p2, p3]
    p_to_publisher = [p4, p5, p6]
    # Signal is sent also to all child processes
    signal.signal(signal.SIGINT, signal_handler)
    print('Press Ctrl+C to stop and exit!')

    Process(target=start_serial_port_reader, name="serial_port_reader", args=(p_to_parser, )).start()
    Process(target=start_data_parser, name="data_parser", args=(p_to_parser, p_to_publisher, )).start()
    Process(target=start_data_publisher, name="data_publisher", args=(p_to_publisher, )).start()
    
    while not shutdown:
        sleep(3)

    # Close all pipes before exiting
    p1.close(), p2.close(), p3.close()
    p4.close(), p5.close(), p6.close()
        
    root_logger.info("Exiting main...")

if __name__ == "__main__":
    main()
