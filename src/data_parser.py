import signal
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
	logging.config.fileConfig('../conf/logging.conf')
	parser_logger = logging.getLogger("parser_logger")
     
def truncate_decimal(number : str, decimals):
    try:
        integer_part, decimal_part = number.split('.')
        truncated_decimal = decimal_part[:decimals]
        return f"{integer_part}.{truncated_decimal}"
    except:
        return number
     
def parse_gps(data):
    values = data.split(',')
    for i in range(len(values)):
        values[i] = truncate_decimal(values[i], 8)
    return (f"GPS,device=kendau_gps lat={values[0]},long={values[1]}")

def parse_ecu(data):
    out = ''
    values = data.split(',')
    ecu_sensors = [
    "engineRunning",
    "steering",
    "abs",
    "gear",
    "clutch_input",
    "throttle_input",
    "brake_input",
    "rpm",
    "wheelspeed",
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

    return (f"ECU,device=control_unit {out}")

def parse_imu(data):
    data = ast.literal_eval(data)
    fields = ['gY', 'gZ', 'aZ', 'aX', 'aY', 'gX']
    out = ''
    
    for entry in fields:
        out = out + entry + '=' + str(data[entry]) + ','

    return (f"IMU,device=gyroscope {out[:-1]}")

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
    
    #parser_logger.debug("[Data parser has to be implemented, doing nothing.]")

    while not shutdown:
        
        empty_counter = 0

        for i in range(3):
            try:        
                # TODO: make sure this stops when buffer is empty
                data = from_serial[i].get(block=False)
                parsed_data = parse_data(i, data)
                to_mqtt[i].put(parsed_data)
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