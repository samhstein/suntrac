import redis, pickle
import sys, json, time
import aws_iot
import base64, zlib
import megaiosun

SECONDS_TO_SAMPLE = 2

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
    aws_iot.sendData(proc_id, 'suntrac/data', j_data)

# eat the first message
pub_sub.get_message()
count = 0

for msg in pub_sub.listen():
    print('got message: ', len(data_points), count)
    # just keep one every minute
    if (count == SECONDS_TO_SAMPLE):
        data_points.append(json.loads(msg['data']))
        count = 0

    # send them up when its just under 1k
    if len(data_points) >= 30:
        send_to_cloud(proc_id, data_points)

    count += 1
    time.sleep(0.1)
