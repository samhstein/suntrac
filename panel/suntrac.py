import redis
import sys, json

# get connection to redis
redis_pub = redis.Redis(host='localhost', port=6379, db=0)
pub_sub = redus_pubsub()
pub_sub.subscribe('suntrac-reading')

for msg in pub_sub.listen():
    print(json.loads(msg))
    time.sleep(0.1)
