import redis
import time, leds, os, sim868, lsm303ctr
import signal, json, aws_iot, sys
import megaiosun

CONFIG_FILE = '/home/pi/suntrac/iot/panel/suntrac_config.json'

connected = True
# get the lights, gprs, and acc
leds = leds.leds()
sim868 = sim868.sim868()
acc_mag = lsm303ctr.lsm303ctr()
proc_id = megaiosun.get_proc_id()
megaiosun_version = megaiosun.version()
pitch = acc_mag.getPitch()

# lets see if were connected
comms = sim868.get_status()
if comms.get('ip') == '0.0.0.0':
    connected = False

print('connected', connected)
time.sleep(3)

def handler_stop_signals(signum, frame):
    print("Stopping Verification")
    leds.lights_off()
    sys.exit()

signal.signal(signal.SIGINT, handler_stop_signals)
signal.signal(signal.SIGTERM, handler_stop_signals)

# both white during startup
leds.lights_on(leds.LED_WHITE_OFF, leds.LED_OFF_WHITE)

# read the config file
with open(CONFIG_FILE, 'r') as json_data_file:
    config = json.load(json_data_file)

# start ppp, send it to the cloud
if connected:
    print('staring ppp.')
    os.system('sudo pppd call gprs')
    time.sleep(15)
    aws_iot = aws_iot.aws_iot(proc_id)
    print('sending config to aws')
    aws_iot.sendData('suntrac/config', config)
    time.sleep(3)
else:
    print('NOT CONNECTED!!!')
    sys.exit()

# update and write the config file
with open(CONFIG_FILE, 'w') as json_data_file:
    print('writing config file...')
    config['proc_id'] = proc_id
    config['comms'] = comms
    config['pitch'] = round(pitch, 1)
    json.dump(config, json_data_file, indent=4)

time.sleep(3)

# start the panel daemon
print('starting suntracd...')
os.system('sudo systemctl start suntracd.service')
time.sleep(10)

# for the data test, just 10 samples per packet, use
# every sample, samples come every 6 seconds
SAMPLES_PER_MINUTE = 1
SAMPLES_PER_PACKET = 10

# get connection to redis
redis_pub = redis.Redis(host='localhost', port=6379, db=0)
pub_sub = redis_pub.pubsub()
pub_sub.subscribe('suntrac-reading')
data_points = []
count = 0

for message in pub_sub.listen():
    # just keep one every ???
    if (count >= SAMPLES_PER_MINUTE):
        print('Got sample from panel.')
        data_points.append(json.loads(message['data']))
        count = 0

    # send them up when its just under 1k
    if len(data_points) >= SAMPLES_PER_PACKET:
        print('Sending data to the cloud.')
        aws_iot.sendData('suntrac/data', data_points)
        data_points.clear()

    count += 1
