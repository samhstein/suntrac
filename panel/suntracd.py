import megaiosun, pytz
import time, sys, datetime, json
from pymemcache.client.base import Client
from pymemcache import serde
from pysolar.solar import *
from timezonefinder import TimezoneFinder
import math
import leds

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

def get_temp_c(v):
    ohms = THERMISTOR_BALANCE / (INPUT_VOLTS / v - 1)
    steinhart = math.log(ohms / THERMISTOR_RO) / THERMISTOR_BETA
    steinhart += 1.0 / (THERMISTOR_TO + 273.15)
    steinhart = (1.0 / steinhart) - 273.15
    return steinhart

def handle_over_temp(temp_inlet, temp_outlet, max_temp, leds):
    print('hot: ', temp_inlet, temp_outlet, max_temp)
    if temp_inlet < max_temp and temp_outlet < max_temp:
        return

    print('hot hot: ', temp_inlet, temp_outlet, max_temp)
    if temp_inlet > max_temp:
        print('inlet too hot: ', temp_inlet)
        leds.lights_on(leds.LED_YELLOW_OFF, leds.LED_OFF_YELLOW)
    elif temp_outlet > max_temp:
        print('outlet too hot: ', temp_inlet)
        leds.lights_on(leds.LED_YELLOW_OFF, leds.LED_OFF_RED)

    megaiosun.set_motor(RELAY_EAST, 1)
    time.sleep(5)
    megaiosun.set_motor(RELAY_EAST, 0)
    _temp_inlet = temp_inlet
    _temp_outlet = temp_outlet
    while _temp_inlet > max_temp or _temp_outlet > max_temp:
        volt_inlet = megaiosun.get_adc_volt(TEMP_INLET)
        _temp_inlet = get_temp_c(volt_inlet)
        volt_outlet = megaiosun.get_adc_volt(TEMP_OUTLET)
        _temp_outlet = get_temp_c(volt_outlet)
        sleep(10)

    leds.lights_on(leds.LED_GREEN_OFF, leds.LED_MASK)


client = Client(('localhost', 11211),
    serializer=serde.python_memcache_serializer,
    deserializer=serde.python_memcache_deserializer)

with open('suntrac.config') as json_data_file:
    config = json.load(json_data_file)

latitude = config.get('latitude')
longitude = config.get('longitude')
max_temp = config.get('max_temp')

tf = TimezoneFinder()
time_zone = tf.timezone_at(lng=longitude, lat=latitude)

volt_outlet = ohms_outlet = temp_outlet = 0
volt_inlet = ohms_inlet = temp_inlet = 0
light_east = light_west = 0
light_error = False
count = 0
over_temp = False

# lets get the sun
date = datetime.datetime.now(pytz.timezone(time_zone))
sun_altitude = get_altitude(latitude, longitude, date)
sun_azimuth = get_azimuth(latitude, longitude, date)

# stop the motors if they are moving
megaiosun.set_motors(0)

# get the lights
leds=leds.leds()
leds.test()
leds.lights_on(leds.LED_GREEN_OFF, leds.LED_MASK)

while True:

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
        time.sleep(.1)


    # just print every x for now, need a timer
    if count * POLL_TIME == 60:
        print('in save to memcached')
        date = datetime.datetime.now(pytz.timezone(time_zone))
        sun_altitude = get_altitude(latitude, longitude, date)
        sun_azimuth = get_azimuth(latitude, longitude, date)
        reading = { 'temp_outlet': temp_outlet, 'temp_inlet': temp_inlet, 'volt_outlet': volt_outlet,
            'volt_inlet': volt_inlet, 'light_east': light_east, 'light_west': light_west, 'photo_diff': photo_diff,
            'time_zone': time_zone, 'timestamp': time.time(), 'sun_altitude': sun_altitude,
            'sun_azimuth': sun_azimuth }
        print(reading)
        client.set('suntrac_reading', reading)
        count = 0

    count += 1
    time.sleep(POLL_TIME)

# stop the motors if they are moving
leds.lights_off()
megaiosun.set_motors(0)
