import paho.mqtt.client as mqtt # type: ignore
import signal
import logging, logging.config
from time import sleep
import multiprocessing

BROKER_ADDR = "85.235.151.197"
BROKER_PORT = 1883
BROKER_UNAME = "rpi-mqtt"
BROKER_PASSWD = "iot-24"

topics = ["Kendau_GPS", "Control_Unit", "Gyroscope"]

shutdown = False

def signal_handler(signal, frame):
	global shutdown
	shutdown = True

def init_logger():
	global publisher_logger
	logging.config.fileConfig('../logging.conf')
	publisher_logger = logging.getLogger("publisher_logger")

def on_connect(self, client, userdata, flags, rc):
    if rc == 0:
        publisher_logger.info(f"Data Publisher succesfully connected to MQTT broker: {BROKER_ADDR}")
    else:
        publisher_logger.critical(f"Failed to connect to MQTT broker. Return code: {rc}")

def start_data_publisher(pipes: list[multiprocessing.Queue]):

    init_logger()

    signal.signal(signal.SIGINT, signal_handler)
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.on_connect = on_connect
    mqttc.username_pw_set(BROKER_UNAME, BROKER_PASSWD)
    mqttc.connect(BROKER_ADDR, BROKER_PORT, keepalive=60)
    mqttc.loop(timeout=1.0)  # check only at the beginning of the connection
    
    while not shutdown:

        empty_counter = 0

        for i in range(3):
            try:
                msg = pipes[i].get(block=False)
                # publisher_logger.info(f"[{topics[i]}]: Received message = {msg}")
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