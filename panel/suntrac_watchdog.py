import RPi.GPIO as GPIO
import time, leds, os, gprs
import signal
import megaiosun

run = True
pushed = False
down_time = last_time = None
push_count = 0
# get the lights, gprs
leds = leds.leds()
gprs = gprs.gprs()

def handler_stop_signals(signum, frame):
    print('in handler')
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
            os.system('sudo shutdown -r now')
            break

    # double push, start node-red
    if last_time and pushed and down_time - last_time < .5:
        leds.lights_on(leds.LED_BLUE_OFF, leds.LED_OFF_BLUE)
        push_count = 0
        os.system('node-red-pi --max-old-space-size=256')
    else:
        push_count = 0


GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(27, GPIO.BOTH, callback=button_push, bouncetime=50)
# both white during startup
leds.lights_on(leds.LED_WHITE_OFF, leds.LED_OFF_WHITE)

# get the config info from the board see if we have
# connectivity that provides lat and long

proc_id = megaiosun.get_proc_id()
megaiosun_version = megaiosun.version()
comms = gprs.get_status()

while run:
    time.sleep(10)
