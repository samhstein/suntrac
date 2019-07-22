import megaiosun, pytz
import time, sys, datetime, json
import redis
from pysolar.solar import *
from timezonefinder import TimezoneFinder
import math, signal
import leds, lsm303ctr

run = True

def handler_stop_signals(signum, frame):
    global run
    run = False

signal.signal(signal.SIGINT, handler_stop_signals)
signal.signal(signal.SIGTERM, handler_stop_signals)

THERMISTOR_TO = 25
THERMISTOR_RO = 86000
THERMISTOR_BALANCE = 100000
THERMISTOR_BETA = 5000
INPUT_VOLTS = 5.0
TEMP_INLET = 1      # adc 1
TEMP_OUTLET = 2     # adc 2
LIGHT_WEST = 3      # adc 3
LIGHT_EAST = 4      # adc 4
RELAY_WEST = 1      # motor 1
RELAY_EAST = 2      # motor 2
DIFF_VOLTS = 0.25
POLL_TIME = 1.0
MOVE_TIME = 0.0005
THREE_HOURS = 3 * 60 * 60

def get_temp_c(v):
    ohms = THERMISTOR_BALANCE / (INPUT_VOLTS / v - 1)
    steinhart = math.log(ohms / THERMISTOR_RO) / THERMISTOR_BETA
    steinhart += 1.0 / (THERMISTOR_TO + 273.15)
    steinhart = (1.0 / steinhart) - 273.15
    return steinhart

def handle_over_temp(temp_inlet, temp_outlet, max_temp, leds):
    if temp_inlet < max_temp and temp_outlet < max_temp:
        return

    if temp_inlet > max_temp:
        leds.lights_on(leds.LED_WHITE_OFF, leds.LED_OFF_GREEN)
    elif temp_outlet > max_temp:
        leds.lights_on(leds.LED_WHITE_OFF, leds.LED_OFF_RED)

    megaiosun.set_motor(RELAY_EAST, 1)
    time.sleep(20)
    megaiosun.set_motor(RELAY_EAST, 0)
    _temp_inlet = temp_inlet
    _temp_outlet = temp_outlet
    while _temp_inlet > max_temp or _temp_outlet > max_temp:
        volt_inlet = megaiosun.get_adc_volt(TEMP_INLET)
        _temp_inlet = get_temp_c(volt_inlet)
        volt_outlet = megaiosun.get_adc_volt(TEMP_OUTLET)
        _temp_outlet = get_temp_c(volt_outlet)
        time.sleep(10)

    leds.lights_on(leds.LED_GREEN_OFF, leds.LED_MASK)

with open('suntrac.config') as json_data_file:
    config = json.load(json_data_file)

latitude = float(config.get('comms').get('lat'))
longitude = float(config.get('comms').get('lng'))
print(latitude, longitude)
max_temp = config.get('max_temp')

tf = TimezoneFinder()
time_zone = tf.timezone_at(lng=longitude, lat=latitude)

volt_outlet = ohms_outlet = temp_outlet = 0
volt_inlet = ohms_inlet = temp_inlet = 0
light_east = light_west = 0
light_error = False
over_temp = False

# lets get the sun
date = datetime.datetime.now(pytz.timezone(time_zone))
sun_altitude = get_altitude(latitude, longitude, date)
sun_azimuth = get_azimuth(latitude, longitude, date)

last_moved = date

# stop the motors if they are moving
megaiosun.set_motors(0)

# get the lights
leds = leds.leds()
leds.test()
leds.lights_on(leds.LED_GREEN_OFF, leds.LED_MASK)

# get the accel
acc_mag = lsm303ctr.lsm303ctr()
initial_roll = acc_mag.getRoll()
mag_ready = acc_mag.isMagReady()
initial_heading = acc_mag.getHeading()
initial_tilt_heading = acc_mag.getTiltHeading()

# get connection to redis
redis_pub = redis.Redis(host='localhost', port=6379, db=0)

while run:

    try:
        volt_outlet = megaiosun.get_adc_volt(TEMP_OUTLET)
        temp_outlet = get_temp_c(volt_outlet)
    except Exception as e:
        leds.lights_on(leds.LED_RED_OFF, leds.LED_OFF_GREEN)
        print('v1 error: ', e)

    try:
        volt_inlet = megaiosun.get_adc_volt(TEMP_INLET)
        temp_inlet = get_temp_c(volt_inlet)
    except Exception as e:
        leds.lights_on(leds.LED_RED_OFF, leds.LED_OFF_RED)
        print('v2 error: ', e)

    handle_over_temp(temp_inlet, temp_outlet, max_temp, leds)

    try:
        light_east = megaiosun.get_adc_volt(LIGHT_EAST)
    except Exception as e:
        light_error = True
        leds.lights_on(leds.LED_WHITE_OFF, leds.LED_RED_OFF)
        print('v3 error: ', e)

    try:
        light_west = megaiosun.get_adc_volt(LIGHT_WEST)
    except Exception as e:
        light_error = True
        leds.lights_on(leds.LED_WHITE_OFF, leds.LED_OFF_GREEN)
        print('v4 error: ', e)

    photo_diff = light_east - light_west

    # if the diff is too big lets move it
    # lets keep it tight
    if abs(photo_diff) > DIFF_VOLTS and light_error != True:
        if photo_diff < 0:
            relay = RELAY_WEST
            leds.lights_on(leds.LED_GREEN_OFF, leds.LED_OFF_GREEN)
        else:
            relay = RELAY_EAST
            leds.lights_on(leds.LED_GREEN_OFF, leds.LED_OFF_RED)

        moving_diff = photo_diff
        megaiosun.set_motor(relay, 1)
        print('start moving... ', relay)
        while abs(moving_diff) > .05:
            moving_diff = megaiosun.get_adc_volt(LIGHT_EAST) - megaiosun.get_adc_volt(LIGHT_WEST)
            time.sleep(MOVE_TIME)

        # turn it off
        print('stop moving...')
        leds.lights_on(leds.LED_GREEN_OFF, leds.LED_MASK)
        megaiosun.set_motor(relay, 0)
        last_moved = datetime.datetime.now(pytz.timezone(time_zone))
        time.sleep(.1)

    # pub every sample
    date = datetime.datetime.now(pytz.timezone(time_zone))
    sun_altitude = get_altitude(latitude, longitude, date)
    sun_azimuth = get_azimuth(latitude, longitude, date)
    reading = { 't_o': round(temp_outlet, 1), 't_i': round(temp_inlet, 1),
        'l_e': light_east, 'l_w': light_west, 'pd': round(photo_diff, 4),
        's_alt': round(sun_altitude,1),'s_az': round(sun_azimuth, 1),
        'ts': round(time.time(), 1),
        'lm': round((date - last_moved).total_seconds(), 1),
        'roll': round(acc_mag.getRoll(), 1) }

    # pub the string
    redis_pub.publish('suntrac-reading', json.dumps(reading))
    if (date - last_moved).total_seconds() > THREE_HOURS:
        megaiosun.set_motor(RELAY_EAST, 1)
        time.sleep(30)
        megaiosun.set_motor(RELAY_EAST, 0)

    time.sleep(POLL_TIME)

# stop the motors if they are moving
leds.lights_off()
megaiosun.set_motors(0)
