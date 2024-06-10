import paho.mqtt.client as mqtt # type: ignore
import signal
import ssl
import logging, logging.config
from time import sleep
import multiprocessing

BROKER_ADDR = "85.235.151.197"
BROKER_PORT = 8883
BROKER_UNAME = "rpi-mqtt"
BROKER_PASSWD = "iot-24"

CLIENT_CERT = "../ssl/client.crt"
CLIENT_KEY = "../ssl/client.key"
CA_CERT = "../ssl/ca.crt"

topics = ["Kendau_GPS", "Control_Unit", "Gyroscope"]

shutdown = False

def signal_handler(signal, frame):
	global shutdown
	shutdown = True

def init_logger():
	global publisher_logger
	logging.config.fileConfig('../logging.conf')
	publisher_logger = logging.getLogger("publisher_logger")

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        publisher_logger.critical(f"Failed to connect to MQTT broker. Return code: {reason_code}")
    else:
        publisher_logger.info(f"Data Publisher succesfully connected to MQTT broker: {BROKER_ADDR}")

def start_data_publisher(pipes: list[multiprocessing.Queue]):

    init_logger()

    signal.signal(signal.SIGINT, signal_handler)
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    
    # TODO: verify what appens in case of TimeOutError
    
    # Transport layer security setup
    mqttc.tls_set(CA_CERT, CLIENT_CERT, CLIENT_KEY, tls_version=mqtt.ssl.PROTOCOL_TLS)
    mqttc.tls_insecure_set(True)

    mqttc.username_pw_set(BROKER_UNAME, BROKER_PASSWD)
    try:
        mqttc.connect(BROKER_ADDR, BROKER_PORT, keepalive=60)
        mqttc.loop_start()
        publisher_logger.info(f"Data Publisher succesfully connected to MQTT broker: {BROKER_ADDR}:{BROKER_PORT}")

    except TimeoutError:
        global shutdown
        shutdown = True
        publisher_logger.critical(f"Data Publisher failed to connect to MQTT broker: Timeout error on {BROKER_ADDR}:{BROKER_PORT}")
    
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