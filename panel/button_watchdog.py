import RPi.GPIO as GPIO
import datetime, time
import leds

pushed = False
# get the lights
leds = leds.leds()

def button_push(input_pin):
    global pushed
    now = datetime.now()
    time_diff = last_time - now
    global last_time = datetime.now()
    pushed = not pushed
    print("button pushed on pin", input_pin, pushed)
    if time_diff > 5:
        leds = leds.leds()
        leds.lights_off()
        print('long push')

GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(27, GPIO.BOTH, callback=button_push)

while True:
    time.sleep(100)
