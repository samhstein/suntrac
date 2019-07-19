import redis, pickle
import sys, json, time
import aws_iot

# get aws_iot
aws_iot = aws_iot.aws_iot()
# get connection to redis
redis_pub = redis.Redis(host='localhost', port=6379, db=0)
pub_sub = redis_pub.pubsub()
pub_sub.subscribe('suntrac-reading')
data_points = []

def send_to_cloud(data_points):
    print(data_points)
    compressed_points = pickle.dumps(data_points)
    print(len(compressed_points))
    data_points.clear()
    # aws_iot.send(compressed_points)

for msg in pub_sub.listen():
    print('got message')
    data_points.append(msg)
    if len(data_points) >= 10:
        send_to_cloud(data_points)

    time.sleep(0.1)
