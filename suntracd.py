import megaio, pytz
import math, time, sys, datetime, json
from pymemcache.client.base import Client
from pymemcache import serde
from pysolar.solar import *
from timezonefinder import TimezoneFinder

THERMISTOR_TO =25
THERMISTOR_RO = 860000
THERMISTOR_BALANCE = 100000
THERMISTOR_BETA = 4000
INPUT_VOLTS = 3.3

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

#megaio.set_relay(0, 2, 1)      #turn on relay 2 on stack level 0

volt_1 = ohms_1 = temp_1 = 0
volt_2 = ohms_2 = temp_2 = 0
volt_3 = volt_4 = 0

while True:
    try:
        volt_1 = megaio.get_adc_volt(0, 5)
        ohms_1 = THERMISTOR_BALANCE * ((INPUT_VOLTS / volt_1) - 1)
        temp_1 = get_temp_c(ohms_1)
    except Exception as e:
        print(e)

    try:
        volt_2 = megaio.get_adc_volt(0, 6)
        ohms_2 = THERMISTOR_BALANCE * ((INPUT_VOLTS / volt_2) - 1)
        temp_2 = get_temp_c(ohms_2)
    except Exception as e:
        print(e)

    volt_3 = megaio.get_adc_volt(0, 7)
    volt_4 = megaio.get_adc_volt(0, 8)

    photo_diff = volt_3 - volt_4

    # let get the sun
    date = datetime.datetime.now(pytz.timezone(time_zone))

    sun_altitude = get_altitude(latitude, longitude, date)
    sun_azimuth = get_azimuth(latitude, longitude, date)


    client.set('suntrac_reading', { 'temp_1': temp_1, 'temp_2': temp_2,
        'volt_3': volt_3, 'volt_4': volt_4, 'photo_diff': photo_diff, 'time_zone': time_zone,
        'timestamp': time.time(), 'sun_altitude': sun_altitude, 'sun_azimuth': sun_azimuth })

    time.sleep(1)
