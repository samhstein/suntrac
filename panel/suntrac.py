import redis, pickle
import sys, json, time
import aws_iot
import base64, zlib

# get aws_iot
aws_iot = aws_iot.aws_iot()
# get connection to redis
redis_pub = redis.Redis(host='localhost', port=6379, db=0)
pub_sub = redis_pub.pubsub()
pub_sub.subscribe('suntrac-reading')
data_points = []

def send_to_cloud(data_points):
    print(data_points)
    j_zipped = {
        "j_zipped": base64.b64encode(
            zlib.compress(
                json.dumps(data_points).encode('utf-8')
            )
        ).decode('ascii')
    }
    print('j_zipped: ', j_zipped, len(j_zipped.get('j_zipped')))
    data_points.clear()
    # aws_iot.send(compressed_points)

# eat the first message
pub_sub.get_message()
for msg in pub_sub.listen():
    data_points.append(json.loads(msg['data']))
    if len(data_points) >= 10:
        send_to_cloud(data_points)

    time.sleep(0.1)
