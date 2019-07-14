from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import requests, json, os

class aws_iot:

    IOT_ENDPOINT = 'a2z6jgzt0eip8f-ats.iot.us-west-2.amazonaws.com'
    CERT_ENDPOINT = 'https://5r874yg6bf.execute-api.us-east-1.amazonaws.com/LATEST/getcert?serialNumber=value1&deviceToken=value2'
    CERT_DIR = '/home/suntrac/certs/'

    def get_cert(self, proc_id):
        end_point = self.CERT_ENDPOINT.replace('value1', proc_id).replace('value2', proc_id[-4:])
        print('in get cert: ', end_point)
        r = requests.get(end_point)
        print('request json: ', r.json())
        certs = r.json()
        with open(CERT_DIR + 'RootCA.pem', 'w') as f:
            f.write(certs.get('RootCA')
        with open(CERT_DIR + 'PrivaveKey.key', 'w') as f:
            f.write(certs.get('PrivateKey')
        with open(CERT_DIR + 'certificatePem.crt', 'w') as f:
            f.write(certs.get('certificatePem')

    # Custom MQTT message callback
    def customCallback(client, userdata, message):
        print("Received a new message: ")
        print(message.payload)
        print("from topic: ")
        print(message.topic)
        print("--------------\n\n")


    def sendData():
        myMQTTClient = AWSIoTMQTTClient(proc_id)
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
