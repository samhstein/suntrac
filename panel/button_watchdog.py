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

    print('27: ', GPIO.input(27))

    while not GPIO.input(27):
        time.sleep(.1)
        if time.time() - down_time > 5:
            print('long push')
            break

    print("button pushed on pin", input_pin, pushed)


GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(27, GPIO.BOTH, callback=button_push, bouncetime=50)

while True:
    time.sleep(100)
