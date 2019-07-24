import RPi.GPIO as GPIO
import time, leds, os, sim868, lsm303ctr
import signal, json, aws_iot, aws_job
import megaiosun
from timeloop import Timeloop
from datetime import timedelta

run = True
pushed = False
connected = True
down_time = last_time = None
push_count = 0
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

certs = {''}
if connected:
    aws_iot = aws_iot.aws_iot(proc_id)
    aws_job = aws_job.aws_job('suntracJobClient', proc_id, aws_iot.get_mqqt_client())

tl = Timeloop()
# time loop for job handler
@tl.job(interval=timedelta(seconds=60))
def check_every_hour():
    print ("current time : ", time.ctime())
    aws_job.check_for_jobs()

def handler_stop_signals(signum, frame):
    global run
    leds.lights_off()
    run = False

signal.signal(signal.SIGINT, handler_stop_signals)
signal.signal(signal.SIGTERM, handler_stop_signals)

def button_push(input_pin):
    global pushed
    global down_time, last_time
    global push_count

    pushed = not pushed

    if pushed:
        push_count += 1
        last_time = down_time
        down_time = time.time()

    # long push, reboot
    while not GPIO.input(27):
        time.sleep(.1)
        if time.time() - down_time > 5:
            leds.lights_off()
            os.system('sudo reboot')
            break

    # double push, start node-red
    if last_time and pushed and down_time - last_time < .5:
        leds.lights_on(leds.LED_BLUE_OFF, leds.LED_OFF_BLUE)
        push_count = 0
        os.system('node-red-pi --max-old-space-size=256')
        os.system('sudo killall pppd')
        os.system('sudo hotspot start')
    else:
        push_count = 0


GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(27, GPIO.BOTH, callback=button_push, bouncetime=50)
# both white during startup
leds.lights_on(leds.LED_WHITE_OFF, leds.LED_OFF_WHITE)


# read the config file
with open('suntrac_config.json', 'r') as json_data_file:
    config = json.load(json_data_file)

certs = config['certs']
if connected:
    certs = aws_iot.get_certs(proc_id)

# update and write the config file
with open('suntrac_config.json', 'w') as json_data_file:
    config['proc_id'] = proc_id
    config['comms'] = comms
    config['certs'] = certs
    config['pitch'] = round(pitch, 1)
    json.dump(config, json_data_file)

# send it to the cloud
if connected:
    aws_iot.sendData('suntrac/config', config)
    tl.start()

while run:
    time.sleep(1)
