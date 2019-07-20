import redis, pickle
import sys, json, time
import aws_iot
import base64, zlib
import megaiosun

# get aws_iot
aws_iot = aws_iot.aws_iot()
# get connection to redis
redis_pub = redis.Redis(host='localhost', port=6379, db=0)
pub_sub = redis_pub.pubsub()
pub_sub.subscribe('suntrac-reading')
data_points = []
proc_id = megaiosun.get_proc_id()

def send_to_cloud(proc_id, data_points):
    j_zipped = {
        "proc_id": proc_id,
        "j_zipped": base64.b64encode(
            zlib.compress(
                json.dumps(data_points).encode('utf-8')
            )
        ).decode('ascii')
    }
    data_points.clear()

    j_data = json.dumps(j_zipped)
    aws_iot.sendData(
        proc_id,
        'suntrac/data',
        j_data
    )
    print('sending: ', len(j_data), ' bytes to aws')

# eat the first message
pub_sub.get_message()
for msg in pub_sub.listen():
    print(msg['data'])
    data_points.append(json.loads(msg['data']))
    print('got message')
    if len(data_points) >= 10:
        send_to_cloud(proc_id, data_points)

    time.sleep(0.1)
