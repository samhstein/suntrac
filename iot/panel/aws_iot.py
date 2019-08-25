from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import requests, json, os, datetime
import base64, zlib

class aws_iot:

    IOT_ENDPOINT = 'a2z6jgzt0eip8f-ats.iot.us-east-1.amazonaws.com'
    CERT_ENDPOINT = 'https://5r874yg6bf.execute-api.us-east-1.amazonaws.com/LATEST/getcert?serialNumber=value1&deviceToken=value2'
    CERT_ROOT = '/home/pi/suntrac/iot/certs/AmazonRootCA1.pem'
    CERT_PRIVATE = '/home/pi/suntrac/iot/certs/PrivateKey.key'
    CERT_CERT = '/home/pi/suntrac/iot/certs/certificatePem.crt'

    def __init__(self, proc_id):
        self.proc_id = proc_id
        self.myMQTTClient = AWSIoTMQTTClient(proc_id)
        self.myMQTTClient.configureEndpoint(self.IOT_ENDPOINT, 8883)
        certs = self.get_certs()
        self.myMQTTClient.configureCredentials(self.CERT_ROOT, self.CERT_PRIVATE, self.CERT_CERT)
        # AWSIoTMQTTClient connection configuration
        self.myMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
        self.myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
        self.myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
        self.myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
        self.myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec


    def get_mqqt_client(self):
        return self.myMQTTClient

    def get_certs(self):
        # if we have one we have em all
        if os.path.exists(self.CERT_CERT):
            return

        end_point = self.CERT_ENDPOINT.replace('value1', self.proc_id).replace('value2', self.proc_id[:6])
        r = requests.get(end_point)
        certs = r.json()
        # update to use the right root cert in the cvm
        with open(self.CERT_PRIVATE, 'w') as f:
            f.write(certs.get('keyPair').get('PrivateKey'))

        with open(self.CERT_CERT, 'w') as f:
            f.write(certs.get('certificatePem'))

        return

    # Custom MQTT message callback
    def customCallback(self, client, userdata, message):
        print("Received a new message: ")
        print(message.payload)
        print("from topic: ")
        print(message.topic)
        print("--------------\n\n")


    def sendData(self, topic, data):
        # zip it up
        j_zipped = {
            "proc_id": self.proc_id,
            "j_zipped": base64.b64encode(
                zlib.compress(
                    json.dumps(data).encode('utf-8')
                )
            ).decode('ascii')
        }
        self.myMQTTClient.connect()
        self.myMQTTClient.publish(topic, json.dumps(j_zipped), 1)
        self.myMQTTClient.subscribe(topic, 1, self.customCallback)
        self.myMQTTClient.unsubscribe(topic)
        self.myMQTTClient.disconnect()
