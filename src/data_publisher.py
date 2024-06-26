import time
import paho.mqtt.client as mqttcl # type: ignore
import signal
import logging, logging.config
from time import sleep
import multiprocessing
import configparser
from queue import Empty

BROKER_ADDR = ""
BROKER_PORT = None
BROKER_UNAME = ""
BROKER_PASSWD = ""

CLIENT_CERT = ""
CLIENT_KEY = ""
CA_CERT = ""

topics = ["Kendau_GPS", "Control_Unit", "Gyroscope"]

connected = False
shutdown = False

def load_conf():
    config = configparser.ConfigParser()
    config.readfp(open(r"../conf/mqtt.conf"))
    global BROKER_ADDR, BROKER_PORT, BROKER_UNAME, BROKER_PASSWD, CLIENT_CERT, CLIENT_KEY, CA_CERT
    BROKER_ADDR = config.get('broker_mqtt', 'BROKER_ADDR')
    BROKER_PORT = int(config.get('broker_mqtt', 'BROKER_PORT'))
    BROKER_UNAME = config.get('broker_mqtt', 'BROKER_UNAME')
    BROKER_PASSWD = config.get('broker_mqtt', 'BROKER_PASSWD')
    CLIENT_CERT = config.get('certificates', 'CLIENT_CERT')
    CLIENT_KEY = config.get('certificates', 'CLIENT_KEY')
    CA_CERT = config.get('certificates', 'CA_CERT')

def on_pre_connect(client, userdata):
    publisher_logger.info("Connection attempt with the broker...")
    sleep(0.5)

def on_connect(client, userdata, flags, reason_code, properties):
    global connected
    if reason_code.is_failure:
        publisher_logger.critical(f"Failed to connect to MQTT broker. Return code: {reason_code}")
        connected = False
    else:
        publisher_logger.info(f"Data Publisher succesfully connected to MQTT broker: {BROKER_ADDR}")
        connected = True


def on_disconnect(client, userdata, flags, reason_code, properties):
    global connected
    publisher_logger.info(f"Client lost connection. Trying to reconnect...")
    connected = False
    while not client.is_connected():
        try:
            client.reconnect()
        except ConnectionRefusedError:
            publisher_logger.error(f"Unable to reconnect to broker. Retrying...")
        

def signal_handler(signal, frame):
	global shutdown
	shutdown = True

def init_logger():
	global publisher_logger
	logging.config.fileConfig('../conf/logging.conf')
	publisher_logger = logging.getLogger("publisher_logger")


def start_data_publisher(pipes: list[multiprocessing.Queue]):
    global shutdown
    global connected
    init_logger()
    load_conf()
    signal.signal(signal.SIGINT, signal_handler)
    mqttc = mqttcl.Client(mqttcl.CallbackAPIVersion.VERSION2)
        
    # Transport layer security setup
    
    mqttc.tls_set(CA_CERT, CLIENT_CERT, CLIENT_KEY, tls_version=mqttcl.ssl.PROTOCOL_TLS)
    mqttc.tls_insecure_set(True)
    mqttc.on_pre_connect = on_pre_connect
    mqttc.on_connect = on_connect
    mqttc.on_disconnect = on_disconnect
    mqttc.reconnect_delay_set(1, 120)
    mqttc.username_pw_set(BROKER_UNAME, BROKER_PASSWD)
    try:
        mqttc.connect(BROKER_ADDR, BROKER_PORT, keepalive=60)
        mqttc.loop_start()
        # waits for connection
        sleep(2)
        empty_slot = [0]*2
        while not shutdown:
            if connected:
                published = 0
                empty_counter = 0

                start = time.time_ns()
                for i in range(3):
                    try:
                        msg = pipes[i].get(block=False)
                        mqttc.publish(topics[i], msg, 0)

                        published += 1
                    except Empty:
                        empty_counter += 1
                    except Exception as e:
                        publisher_logger.critical(f"Unknown exception: {e}")
                
                if empty_counter == 3:
                    # checks empty history
                    if empty_slot[0] == 3 and empty_slot[1] == 3: 
                        sleep(2.95)
                
                sleep(0.045)

                # update empty slot array with current value (left rotation by 1)
                empty_slot[0] = empty_slot[1]
                empty_slot[1] = empty_counter
                
                end = time.time_ns()
                time_spent = "{:.4f}".format(float((end - start) * (10**-9) ))
                publisher_logger.debug(f"Published {published} messages in {time_spent} seconds.")
            else:
                sleep(3)
            
    except ConnectionRefusedError:
        publisher_logger.critical(f"Connection Refused: {BROKER_ADDR}:{BROKER_PORT}")
        shutdown = True
    
    for p in pipes:
        p.cancel_join_thread()
        p.close()
    
    publisher_logger.info("Closing Data Publisher...")