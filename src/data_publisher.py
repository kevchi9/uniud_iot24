import paho.mqtt.client as mqtt # type: ignore
import signal
import logging, logging.config
from time import sleep
import multiprocessing

BROKER_ADDR = "127.0.0.1"
BROKER_PORT = 1883

topics = ["Kendau_GPS", "Control_Unit", "Gyroscope"]

shutdown = False

def signal_handler(signal, frame):
	global shutdown
	shutdown = True

def init_logger():
	global publisher_logger
	logging.config.fileConfig('../logging.conf')
	publisher_logger = logging.getLogger("publisher_logger")

def start_data_publisher(pipes: list[multiprocessing.Queue]):

    init_logger()

    signal.signal(signal.SIGINT, signal_handler)
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.connect(BROKER_ADDR, BROKER_PORT, keepalive=60)

    publisher_logger.info(f"Data Publisher succesfully connected to MQTT broker: {BROKER_ADDR}")
    
    while not shutdown:

        empty_counter = 0

        for i in range(3):
            try:
                msg = pipes[i].get(block=False)
                publisher_logger.info(f"[{topics[i]}]: Received message = {msg}")
                mqttc.publish(topics[i], msg)
            except:
                # publisher_logger.error("Error while reading message from pipe.")
                empty_counter += 1 
                
        if empty_counter == 3:
            sleep(3) 
    
    for p in pipes:
        p.cancel_join_thread()
        p.close()
    
    publisher_logger.info("Closing Data Publisher...")