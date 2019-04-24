import megaiosun, pytz
import time, sys, datetime, json
from pymemcache.client.base import Client
from pymemcache import serde
from pysolar.solar import *
from timezonefinder import TimezoneFinder
import math

THERMISTOR_TO = 25
THERMISTOR_RO = 86000
THERMISTOR_BALANCE = 100000
THERMISTOR_BETA = 5000
INPUT_VOLTS = 5.0
TEMP_1_ADC = 1
TEMP_2_ADC = 2
LIGHT_1_ADC = 3
LIGHT_2_ADC = 4
DIFF_VOLTS = 0.2
RELAY_1 = 1
RELAY_2 = 2
POLL_TIME = 0.5
MOVE_TIME = 0.05

def get_temp_c(r):
    steinhart = math.log(r / THERMISTOR_RO) / THERMISTOR_BETA
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

volt_1 = ohms_1 = temp_1 = 0
volt_2 = ohms_2 = temp_2 = 0
volt_3 = volt_4 = 0
light_error = False
count = 0

while True:
    print(count)
    try:
        volt_1 = megaiosun.get_adc_volt(TEMP_1_ADC)
        ohms_1 = THERMISTOR_BALANCE * ((INPUT_VOLTS / volt_1) - 1)
        temp_1 = get_temp_c(ohms_1)
    except Exception as e:
        print('v1 error')
        print(e)

    try:
        volt_2 = megaiosun.get_adc_volt(TEMP_2_ADC)
        ohms_2 = THERMISTOR_BALANCE * ((INPUT_VOLTS / volt_2) - 1)
        temp_2 = get_temp_c(ohms_2)
    except Exception as e:
        print('v2 error')
        print(e)

    try:
        volt_3 = megaiosun.get_adc_volt(LIGHT_1_ADC)
    except Exception as e:
        light_error = True
        print('v3 error')
        print(e)


    try:
        volt_4 = megaiosun.get_adc_volt(LIGHT_2_ADC)
    except Exception as e:
        light_error = True
        print('v4 error')
        print(e)

    photo_diff = volt_3 - volt_4

    # if the diff is too big lets move it
    # lets keep it tight
    if abs(photo_diff) > DIFF_VOLTS and light_error != True:
        relay = RELAY_2 if photo_diff < 0 else RELAY_1
        moving_relay = relay
        megaiosun.set_motor(relay, 1)
        while relay == moving_relay:
            moving_diff = megaiosun.get_adc_volt(LIGHT_1_ADC) - megaiosun.get_adc_volt(LIGHT_2_ADC)
            moving_relay = RELAY_2 if moving_diff < 0 else RELAY_1
            time.sleep(MOVE_TIME)

        # turn it off
        megaiosun.set_motor(relay, 0)

    # lets get the sun
    date = datetime.datetime.now(pytz.timezone(time_zone))

    sun_altitude = get_altitude(latitude, longitude, date)
    sun_azimuth = get_azimuth(latitude, longitude, date)

    reading = { 'temp_1': temp_1, 'temp_2': temp_2, 'volt_1': volt_1,
        'volt_2': volt_2, 'volt_3': volt_3, 'volt_4': volt_4, 'photo_diff': photo_diff,
        'time_zone': time_zone, 'timestamp': time.time(), 'sun_altitude': sun_altitude,
        'sun_azimuth': sun_azimuth }

    print(reading)

    client.set('suntrac_reading', reading)

    # just print every x for now, need a timer
    if count * POLL_TIME == 60:
        print(reading)
        count = 0

    time.sleep(POLL_TIME)
