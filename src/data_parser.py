import signal
import time
import logging, logging.config
from time import sleep
import multiprocessing
import json

shutdown = False

def signal_handler(signal, frame):
	global shutdown
	shutdown = True

def init_logger():
	global parser_logger
	logging.config.fileConfig('../logging.conf')
	parser_logger = logging.getLogger("parser_logger")
     
def truncate_decimal(number : str, decimals=5):
    integer_part, decimal_part = number.split('.')
    truncated_decimal = decimal_part[:decimals]
    return f"{integer_part}.{truncated_decimal}"
     
def parse_gps(data):
    values = data.split(',')
    for value in values:
         value = truncate_decimal(value)
    return (f"GPS, lat={value[0]},long={value[1]}")

# TODO: implement this
def parse_ecu(data):
    return data

def parse_imu(data):
    data = json.loads(data)
    parsed_data = f"x={data['x']},y={data['y']},z={data['z']}"
    return (f"IMU, {parsed_data}")

#spaces and commas are crucial to respect influx db line protocol, do not change those
def parse_data(sensor, data, timestamp):
    if sensor == 0:
        parsed_data = parse_gps(data)
    elif sensor == 1:
        parsed_data = parse_ecu(data)
    elif sensor == 2:
        parsed_data = parse_imu(data)
    else:
        parser_logger.info("Parsing not specified for input sensor")
    
    return parsed_data + ' ' + str(timestamp)

def start_data_parser(from_serial: list[multiprocessing.Queue], to_mqtt: list[multiprocessing.Queue]):
    signal.signal(signal.SIGINT, signal_handler)
    init_logger()
    
    parser_logger.debug("[Data parser has to be implemented, doing nothing.]")

    while not shutdown:
        
        empty_counter = 0

        for i in range(3):
            try:        
                # TODO: make sure this stops when buffer is empty
                data = from_serial[i].get(block=False)
                timestamp = 0
                parsed_data = parse_data(i, data, timestamp)
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