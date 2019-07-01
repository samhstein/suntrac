import RPi.GPIO as GPIO
import time, leds

pushed = False
down_time = None
push_count = 0
# get the lights
leds = leds.leds()

def button_push(input_pin):
    global pushed
    global down_time
    global push_count

    pushed = not pushed
    if pushed:
        down_time = time.time()
        time.sleep(5)
        print('still down')

    if not pushed:
        push_count += 1

    print("button pushed on pin", input_pin, pushed)


GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(27, GPIO.BOTH, callback=button_push, bouncetime=50)

while True:
    time.sleep(100)
