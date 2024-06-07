import signal
import time
import logging, logging.config
from time import sleep
import multiprocessing
import ast

shutdown = False

def signal_handler(signal, frame):
	global shutdown
	shutdown = True

def init_logger():
	global parser_logger
	logging.config.fileConfig('../logging.conf')
	parser_logger = logging.getLogger("parser_logger")
     
def truncate_decimal(number : str, decimals=5):
    try:
        integer_part, decimal_part = number.split('.')
        truncated_decimal = decimal_part[:decimals]
        return f"{integer_part}.{truncated_decimal}"
    except:
        return number
     
def parse_gps(data):
    values = data.split(',')
    for i in range(len(values)):
        values[i] = truncate_decimal(values[i])
    return (f"GPS, lat={values[0]},long={values[1]}")

# TODO: implement this
def parse_ecu(data):
    out = ''
    values = data.split(',')
    ecu_sensors = [
    "airflowspeed",
    "engineRunning",
    "steering",
    "abs",
    "gear",
    "clutch_input",
    "throttle_input",
    "brake_input",
    "rpm",
    "wheelspeed",
    "esc_active",
    "oil_temperature",
    "water_temperature",
    "FL_CoreTemperature",
    "FL_SurfaceTemperature",
    "RL_CoreTemperature",
    "RL_SurfaceTemperature",
    "RR_CoreTemperature",
    "RR_SurfaceTemperature",
    "FR_CoreTemperature",
    "FR_SurfaceTemperature"]

    for i in range(len(values)-1):
        values[i] = truncate_decimal(values[i], 3)

        if i < len(values) - 2:
            out = out + ecu_sensors[i] + '=' + values[i] + ','
        else:
            out = out + ecu_sensors[i] + '=' + values[i]

    return (f"ECU, {out}")

def parse_imu(data):
    data = ast.literal_eval(data)
    parsed_data = f"x={round(data['x'], 3)},y={round(data['y'], 3)},z={round(data['z'], 3)}"
    return (f"IMU, {parsed_data}")

#spaces and commas are crucial to respect influx db line protocol, do not change those
def parse_data(sensor, data):
    values = data.split(',', 1)

    if sensor == 0:
        parsed_data = parse_gps(values[1])
    elif sensor == 1:
        parsed_data = parse_ecu(values[1])
    elif sensor == 2:
        parsed_data = parse_imu(values[1])
    
    return parsed_data + ' ' + values[0]

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
                parsed_data = parse_data(i, data)
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