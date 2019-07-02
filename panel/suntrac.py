from pymemcache.client.base import Client
from pymemcache import serde
import sys

client = Client(('localhost', 11211),
    serializer=serde.python_memcache_serializer,
    deserializer=serde.python_memcache_deserializer)

result = str(client.get('suntrac_reading'))
sys.stdout.write(result.replace("'", '"'))
