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
LIGHT_EAST = 3      # adc 3
LIGHT_WEST = 4      # adc 4
RELAY_WEST = 1      # motor 1
RELAY_EAST = 2      # motor 2
DIFF_VOLTS = 0.1
POLL_TIME = 1.0
MOVE_TIME = 0.01

def get_temp_c(v):
    ohms = THERMISTOR_BALANCE / (INPUT_VOLTS / v - 1)
    steinhart = math.log(ohms / THERMISTOR_RO) / THERMISTOR_BETA
    steinhart += 1.0 / (THERMISTOR_TO + 273.15)
    steinhart = (1.0 / steinhart) - 273.15
    return steinhart

client = Client(('localhost', 11211),
    serializer=serde.python_memcache_serializer,
    deserializer=serde.python_memcache_deserializer)

with open('suntrac.config') as json_data_file:
    config = json.load(json_data_file)

latitude = config.get('latitude')
longitude = config.get('longitude')

tf = TimezoneFinder()
time_zone = tf.timezone_at(lng=longitude, lat=latitude)

volt_outlet = ohms_outlet = temp_outlet = 0
volt_inlet = ohms_inlet = temp_inlet = 0
light_east = light_west = 0
light_error = False
count = 0

# lets get the sun
date = datetime.datetime.now(pytz.timezone(time_zone))
sun_altitude = get_altitude(latitude, longitude, date)
sun_azimuth = get_azimuth(latitude, longitude, date)

# stop the motors if they are moving
megaiosun.set_motors(0)

# get the lights
leds=leds.leds()
leds.lights_off()
leds.lights_on(leds.LED_GREEN_OFF, leds.LED_MASK)

while True:
    print('top of loop: ', count)

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

    print(
        'vto: ', volt_outlet, temp_outlet,
        'vti: ', volt_inlet, temp_inlet,
        'lewde: ', light_east, light_west, photo_diff, light_error
    )

    # if the diff is too big lets move it
    # lets keep it tight
    if abs(photo_diff) > DIFF_VOLTS and light_error != True:
        relay = RELAY_WEST if photo_diff < 0 else RELAY_EAST
        moving_relay = relay
        megaiosun.set_motor(relay, 1)
        print('start moving... ', relay, moving_relay)
        while relay == moving_relay:
            moving_diff = megaiosun.get_adc_volt(LIGHT_EAST) - megaiosun.get_adc_volt(LIGHT_WEST)
            moving_relay = RELAY_WEST if moving_diff < 0 else RELAY_EAST
            time.sleep(MOVE_TIME)

        # turn it off
        print('stop moving...')
        megaiosun.set_motor(relay, 0)



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
