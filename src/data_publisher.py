import paho.mqtt.client as mqtt # type: ignore
import signal

BROKER_ADDR = "127.0.0.1"
BROKER_PORT = 1883

shutdown = False

def signal_handler(signal, frame):
	global shutdown
	shutdown = True

def start_data_publisher(pipe):

    signal.signal(signal.SIGINT, signal_handler)
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.connect(BROKER_ADDR, BROKER_PORT, keepalive=60)

    print(f"Data Publisher succesfully connected to MQTT broker: {BROKER_ADDR}")
    
    while not shutdown:
        try:
            msg = pipe.recv()
            # TODO: manage 3 channels and send messages on 3 different topics
            mqttc.publish("TOPIC1", msg)
        except Exception:
            print("No messages")
            
    pipe.close()
    print("Closing Data Publisher...")

    