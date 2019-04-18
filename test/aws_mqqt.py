from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)


IOT_ENDPOINT = 'a2z6jgzt0eip8f-ats.iot.us-west-2.amazonaws.com'

# Custom MQTT message callback
def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")


myMQTTClient = AWSIoTMQTTClient('beta')
myMQTTClient.configureEndpoint(IOT_ENDPOINT, 8883)
myMQTTClient.configureCredentials(
    "/home/pi/suntrac/certs/root/AmazonRootCA1.pem",
    "/home/pi/suntrac/certs/devices/90c9b2ae5d-private.pem.key",
    "/home/pi/suntrac/certs/devices/90c9b2ae5d-certificate.pem.crt"
    )
myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

myMQTTClient.connect()
myMQTTClient.publish("iot/helo", {'proc_id': proc_id}, 0)
myMQTTClient.subscribe("iot/helo", 1, customCallback)
myMQTTClient.unsubscribe("iot/helo")
myMQTTClient.disconnect()
