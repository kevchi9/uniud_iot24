import signal
import time
import logging, logging.config
from time import sleep
import multiprocessing

shutdown = False

def signal_handler(signal, frame):
	global shutdown
	shutdown = True

def init_logger():
	global parser_logger
	logging.config.fileConfig('../logging.conf')
	parser_logger = logging.getLogger("parser_logger")
     
# TODO: implement this
def parse_data(data):
    return data

def start_data_parser(from_serial: list[multiprocessing.Queue], to_mqtt: list[multiprocessing.Queue]):
    signal.signal(signal.SIGINT, signal_handler)
    init_logger()
    
    parser_logger.debug("[Data parser has to be implemented, doing nothing.]")

    while not shutdown:
        
        empty_counter = 0

        for i in range(3):
            try:        
                data = from_serial[i].get(block=False)
                parsed_data = parse_data(data)
                # Not actually parsed, function has to be implemented
                to_mqtt[i].put(f"Parsed data: {parsed_data}")
                time.sleep(0.05) 
            except:
                # parser_logger.error("Error while reading message from pipe.")
                empty_counter += 1
            
        if empty_counter == 3:
             sleep(3)

    for pipe in from_serial:
        pipe.cancel_join_thread()
        pipe.close()

    for pipe in to_mqtt:
        pipe.cancel_join_thread()
        pipe.close()
            
    parser_logger.info("Closing Data Parser...")