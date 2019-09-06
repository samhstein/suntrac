import megaiosun, pytz
import time, sys, datetime, json
import redis
from pysolar.solar import *
from timezonefinder import TimezoneFinder
import math, signal
import leds, lsm303ctr
from timeloop import Timeloop
from datetime import timedelta

class SuntracPanel:

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
    leds = leds.leds()
    acc_mag = lsm303ctr.lsm303ctr()
    redis_pub = redis.Redis(host='localhost', port=6379, db=0)

    tl = Timeloop()

    def __init__(self,):
        with open('suntrac_config.json') as json_data_file:
            config = json.load(json_data_file)

        self.latitude = float(config.get('comms').get('lat'))
        self.longitude = float(config.get('comms').get('lng'))
        self.max_temp = config.get('max_temp')
        self.connected = False if config.get('comms').get('ip') == '0.0.0.0' else True
        self.connected_color = self.leds.LED_GREEN_OFF if self.connected else self.leds.LED_BLUE_OFF

        tf = TimezoneFinder()
        self.time_zone = tf.timezone_at(lng=self.longitude, lat=self.latitude)

        self.volt_outlet = self.ohms_outlet = self.temp_outlet = 0
        self.volt_inlet = self.ohms_inlet = self.temp_inlet = 0
        self.light_east = self.light_west = 0
        self.light_error = False
        self.over_temp = False
        self.nite_mode = False

        # lets get the sun
        date = datetime.datetime.now(pytz.timezone(self.time_zone))
        self.sun_altitude = get_altitude(self.latitude, self.longitude, date)
        self.sun_azimuth = get_azimuth(self.latitude, self.longitude, date)

        self.last_moved = date

        # stop the motors if they are moving
        megaiosun.set_motors(0)

        # get the lights
        self.leds.test()
        self.leds.lights_on(self.connected_color, self.leds.LED_MASK)

        # get the accel
        self.initial_roll = self.acc_mag.getRoll()
        self.mag_ready = self.acc_mag.isMagReady()
        self.initial_heading = self.acc_mag.getHeading()
        self.initial_tilt_heading = self.acc_mag.getTiltHeading()
        # time loop
        self.tl._add_job(self.publish_panel_data, interval=timedelta(seconds=6))
        self.tl._add_job(self.get_panel_data, interval=timedelta(seconds=1))

    def get_temp_c(self, v):
        ohms = self.THERMISTOR_BALANCE / (self.INPUT_VOLTS / v - 1)
        steinhart = math.log(ohms / self.THERMISTOR_RO) / self.THERMISTOR_BETA
        steinhart += 1.0 / (self.THERMISTOR_TO + 273.15)
        steinhart = (1.0 / steinhart) - 273.15
        return steinhart

    def handle_over_temp(self):
        if self.temp_inlet < self.max_temp and self.temp_outlet < self.max_temp:
            return

        if self.temp_inlet > self.max_temp:
            self.leds.lights_on(self.leds.LED_WHITE_OFF, self.leds.LED_OFF_GREEN)
        elif self.temp_outlet > self.max_temp:
            self.leds.lights_on(self.leds.LED_WHITE_OFF, self.leds.LED_OFF_RED)

        megaiosun.set_motor(self.RELAY_EAST, 1)
        time.sleep(20)
        megaiosun.set_motor(self.RELAY_EAST, 0)
        _temp_inlet = self.acc_magtemp_inlet
        _temp_outlet = self.temp_outlet
        while _temp_inlet > self.max_temp or _temp_outlet > self.max_temp:
            self.volt_inlet = megaiosun.get_adc_volt(self.TEMP_INLET)
            _temp_inlet = self.get_temp_c(self.volt_inlet)
            self.volt_outlet = megaiosun.get_adc_volt(self.TEMP_OUTLET)
            _temp_outlet = self.get_temp_c(self.volt_outlet)
            time.sleep(10)

        self.leds.lights_on(self.leds.LED_GREEN_OFF, self.leds.LED_MASK)

    # pub the string
    def publish_panel_data(self):
        date = datetime.datetime.now(pytz.timezone(self.time_zone))
        sun_altitude = get_altitude(self.latitude, self.longitude, date)
        sun_azimuth = get_azimuth(self.latitude, self.longitude, date)
        reading = { 't_o': round(self.temp_outlet, 1), 't_i': round(self.temp_inlet, 1),
            'l_e': self.light_east, 'l_w': self.light_west, 'pd': round(self.photo_diff, 4),
            's_alt': round(self.sun_altitude,1),'s_az': round(self.sun_azimuth, 1),
            'ts': round(time.time(), 1),
            'lm': round((date - self.last_moved).total_seconds(), 1),
            'roll': round(self.acc_mag.getRoll(), 1),
            'nm': self.nite_mode
        }
        self.redis_pub.publish('suntrac-reading', json.dumps(reading))

    def get_panel_data(self):
        try:
            self.volt_outlet = megaiosun.get_adc_volt(self.TEMP_OUTLET)
            self.temp_outlet = self.get_temp_c(self.volt_outlet)
        except Exception as e:
            self.leds.lights_on(self.leds.LED_RED_OFF, self.leds.LED_OFF_GREEN)
            print('v1 error: ', e)

        try:
            self.volt_inlet = megaiosun.get_adc_volt(self.TEMP_INLET)
            self.temp_inlet = self.get_temp_c(self.volt_inlet)
        except Exception as e:
            self.leds.lights_on(self.leds.LED_RED_OFF, self.leds.LED_OFF_RED)
            print('v2 error: ', e)

        self.handle_over_temp()

        try:
            self.light_east = megaiosun.get_adc_volt(self.LIGHT_EAST)
        except Exception as e:
            self.light_error = True
            self.leds.lights_on(self.leds.LED_WHITE_OFF, self.leds.LED_RED_OFF)
            print('v3 error: ', e)

        try:
            self.light_west = megaiosun.get_adc_volt(self.LIGHT_WEST)
        except Exception as e:
            self.light_error = True
            self.leds.lights_on(self.leds.LED_WHITE_OFF, self.leds.LED_OFF_GREEN)
            print('v4 error: ', e)

        self.photo_diff = self.light_east - self.light_west

        # if the diff is too big lets move it
        # lets keep it tight
        if abs(self.photo_diff) > self.DIFF_VOLTS and self.light_error != True:
            if self.photo_diff < 0:
                relay = self.RELAY_WEST
                self.leds.lights_on(self.leds.LED_GREEN_OFF, self.leds.LED_OFF_GREEN)
            else:
                relay = self.RELAY_EAST
                self.leds.lights_on(self.leds.LED_GREEN_OFF, self.leds.LED_OFF_RED)

            if self.nite_mode and relay = self.RELAY_EAST:
                return

            self.nite_mode = False

            moving_diff = self.photo_diff
            megaiosun.set_motor(relay, 1)
            print('start moving... ', relay)
            while abs(moving_diff) > .05:
                moving_diff = megaiosun.get_adc_volt(self.LIGHT_EAST) - megaiosun.get_adc_volt(self.LIGHT_WEST)
                time.sleep(self.MOVE_TIME)

            # turn it off
            print('stop moving...')
            self.leds.lights_on(self.leds.LED_GREEN_OFF, self.leds.LED_MASK)
            megaiosun.set_motor(relay, 0)
            self.last_moved = datetime.datetime.now(pytz.timezone(self.time_zone))
            time.sleep(.1)

        # turn it east if its dark
        date = datetime.datetime.now(pytz.timezone(self.time_zone))
        if (date - self.last_moved).total_seconds() > self.THREE_HOURS:
            megaiosun.set_motor(self.RELAY_EAST, 1)
            time.sleep(30)
            megaiosun.set_motor(self.RELAY_EAST, 0)
            self.nite_mode = True


if __name__ == "__main__":
    sp = SuntracPanel()
    sp.tl.start(block=True)
    sp.leds.lights_off()
    megaiosun.set_motors(0)
