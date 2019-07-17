from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging, time, pickle

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)


IOT_ENDPOINT = 'a2z6jgzt0eip8f-ats.iot.us-east-1.amazonaws.com'

# Custom MQTT message callback
def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")


proc_id = '01000b000e43484734303420'
myMQTTClient = AWSIoTMQTTClient(proc_id)
myMQTTClient.configureEndpoint(IOT_ENDPOINT, 8883)
myMQTTClient.configureCredentials(
    "/home/pi/suntrac/certs/root/AmazonRootCA1.pem",
    "/home/pi/suntrac/certs/PrivateKey.key",
    "/home/pi/suntrac/certs/certificatePem.crt"
    )

# AWSIoTMQTTClient connection configuration
myMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

data = {"proc_id": proc_id, "raw_data": "hello from device"}
pickled_data = pickle.dumps(data)

myMQTTClient.connect()
myMQTTClient.publish("suntrac/data", pickled_data, 1)
myMQTTClient.subscribe("suntrac/data", 1, customCallback)
myMQTTClient.unsubscribe("suntrac/data")
myMQTTClient.disconnect()

time.sleep(30)
