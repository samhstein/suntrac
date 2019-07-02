import RPi.GPIO as GPIO
import time, leds, os
import signal

run = True
pushed = False
down_time = last_time = None
push_count = 0
# get the lights
leds = leds.leds()

def handler_stop_signals(signum, frame):
    global run
    run = False

signal.signal(signal.SIGINT, handler_stop_signals)
signal.signal(signal.SIGTERM, handler_stop_signals)

def button_push(input_pin):
    global pushed
    global down_time, last_time
    global push_count

    pushed = not pushed
    print("button pushed on pin", input_pin, pushed)

    if pushed:
        push_count += 1
        last_time = down_time
        down_time = time.time()

    # long push
    while not GPIO.input(27):
        time.sleep(.1)
        if time.time() - down_time > 5:
            print('long push')
            leds.lights_off()
            os.system('sudo shutdown -r now')
            break

    # double push
    if last_time and down_time - last_time < .5:
        print('double push', push_count)
        leds.lights_on(leds.LED_BLUE_OFF, leds.LED_OFF_BLUE)
    else:
        push_count = 0


GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(27, GPIO.BOTH, callback=button_push, bouncetime=50)

while run:
    time.sleep(100)
