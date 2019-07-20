from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import requests, json, os

class aws_iot:

    IOT_ENDPOINT = 'a2z6jgzt0eip8f-ats.iot.us-east-1.amazonaws.com'
    CERT_ENDPOINT = 'https://5r874yg6bf.execute-api.us-east-1.amazonaws.com/LATEST/getcert?serialNumber=value1&deviceToken=value2'
    CERT_ROOT = '/home/pi/suntrac/certs/RootCA.crt'
    CERT_PRIVATE = '/home/pi/suntrac/certs/PrivateKey.crt'
    CERT_CERT = '/home/pi/suntrac/certs/certificatePem.crt'

    def get_certs(self, proc_id):
        private, cert, root = None
        # if we have one we have em all
        if os.path.exists(self.CERT_CERT):
            return ({ "certs": { "private": self.CERT_PRIVATE, "cert": self.CERT_CERT, "root": self.CERT_ROOT }})

        end_point = self.CERT_ENDPOINT.replace('value1', proc_id).replace('value2', proc_id[-4:])
        print('in get cert: ', end_point)
        r = requests.get(end_point)
        print('request json: ', r.json())
        certs = r.json()
        with open(self.CERT_DIR + 'RootCA.pem', 'w') as f:
            f.write(certs.get('RootCA'))
            root = f.name

        with open(self.CERT_DIR + 'PrivateKey.key', 'w') as f:
            f.write(certs.get('keyPair').get('PrivateKey'))
            private = f.name

        with open(self.CERT_DIR + 'certificatePem.crt', 'w') as f:
            f.write(certs.get('certificatePem'))
            cert = f.name

        return ({ "certs": { "private": private, "cert": cert, "root": root}})

    # Custom MQTT message callback
    def customCallback(self, client, userdata, message):
        print("Received a new message: ")
        print(message.payload)
        print("from topic: ")
        print(message.topic)
        print("--------------\n\n")


    def sendData(self, proc_id, topic, data):
        myMQTTClient = AWSIoTMQTTClient(proc_id)
        myMQTTClient.configureEndpoint(self.IOT_ENDPOINT, 8883)
        myMQTTClient.configureCredentials(
            self.CERT_DIR + "AmazonRootCA1.pem",
            self.CERT_DIR + "PrivateKey.key",
            self.CERT_DIR + "certificatePem.crt"
            )

        # AWSIoTMQTTClient connection configuration
        myMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
        myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
        myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
        myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
        myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

        myMQTTClient.connect()
        print('sendData: ', topic, data, len(data))
        myMQTTClient.publish(topic, data, 1)
        myMQTTClient.subscribe(topic, 1, self.customCallback)
        myMQTTClient.unsubscribe(topic)
        myMQTTClient.disconnect()
