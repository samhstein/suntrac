import redis, pickle
import sys, json, time
import aws_iot
import base64, zlib
import megaiosun

SAMPLES_PER_MINUTE = 10
SAMPLES_PER_PACKET = 20

# get connection to redis
redis_pub = redis.Redis(host='localhost', port=6379, db=0)
pub_sub = redis_pub.pubsub()
pub_sub.subscribe('suntrac-reading')
data_points = []
proc_id = megaiosun.get_proc_id()
# get aws_iot
aws_iot = aws_iot.aws_iot(proc_id)

# eat the first message
pub_sub.get_message()
count = 0

for message in pub_sub.listen():
    print(time.ctime(), count)
    # just keep one every ???
    if (count >= SAMPLES_PER_MINUTE):
        data_points.append(json.loads(message['data']))
        count = 0

    # send them up when its just under 1k
    if len(data_points) >= SAMPLES_PER_PACKET:
        aws_iot.sendData('suntrac/data', data_points)
        data_points.clear()

    count += 1
