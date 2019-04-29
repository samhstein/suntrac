
#
#  control leds on the expansion board
#

import time,sys
import smbus

class leds:
    IO_EXP_ADD = 0x20
    IO_EXP_DIR = 0x03
    IO_EXP_OUT = 0x01

    ledList = [0, 0x12, 0x24, 0x48, 0x7e, 0x10, 0x20, 0x40, 0x02, 0x04, 0x08, 0x00]
    bus = smbus.SMBus(1)
    loop = False

    # Set up the lights
    def __init__(self,):
        try:
            self.write_data(0x00)
        except Exception as e:
            print("Failed to communicate with I/O expander! " + str(e))

    def write_data(self, data):
        self.bus.write_byte_data(self.IO_EXP_ADD, self.IO_EXP_OUT, data)

    def light_on(self, data):
        self.write_data(~self.ledList[data])

    def lights_off(self):
        self.write_data(0xff)

    def test(self):
        self.loop = True
        while self.loop:
            for i in self.ledList:
                time.sleep(0.5)
                self.bus.write_byte_data(self.IO_EXP_ADD, self.IO_EXP_OUT, ~i) #set output

        self.bus.write_byte_data(IO_EXP_ADD, IO_EXP_OUT, 0xff)

    def stop_test(self):
        self.loop = False
