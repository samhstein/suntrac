#!/usr/bin/env python
#
# GrovePi Library for using the Grove - 6-Axis Accelerometer&Compass v2.0(http://www.seeedstudio.com/depot/Grove-6Axis-AccelerometerCompass-v20-p-2476.html)
#
# This sensor uses LSM303D chip and the library works in Python for the Raspberry Pi
#
# The GrovePi connects the Raspberry Pi and Grove sensors.  You can learn more about GrovePi here:  http://www.dexterindustries.com/GrovePi
#
# Have a question about this library?  Ask on the forums here:  http://forum.dexterindustries.com/c/grovepi
#

# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information see https://github.com/DexterInd/GrovePi/blob/master/LICENSE

import time,sys
import RPi.GPIO as GPIO
import smbus
import math

# use the bus that matches your raspi version
bus =smbus.SMBus(1)

class lsm303d:
    ACC_ADDR        = 0x1D
    MAG_ADDR        = 0x1E

    # accel registers
    ACC_TEMP_L       = 0x0B
    ACC_TEMP_H       = 0x0C
    ACC_ACT_TSH      = 0x1E
    ACC_ACT_DUR      = 0x1F
    ACC_WHO_AM_I     = 0x0F
    ACC_CTRL1        = 0x20
    ACC_CTRL2        = 0x21
    ACC_CTRL3        = 0x22
    ACC_CTRL4        = 0x23
    ACC_CTRL5        = 0x24
    ACC_CTRL6        = 0x25
    ACC_CTRL7        = 0x26
    ACC_STATUS       = 0x27
    ACC_OUT_X_L      = 0x28
    ACC_OUT_X_H      = 0x29
    ACC_OUT_Y_L      = 0x2A
    ACC_OUT_Y_H      = 0x2B
    ACC_OUT_Z_L      = 0x2C
    ACC_OUT_Z_H      = 0x2D
    ACC_FIFO_CTRL    = 0x2E
    ACC_FIFO_SRC     = 0x2F
    ACC_IG_CFG1      = 0x30
    ACC_IG_SRC1      = 0x31
    ACC_IG_THS_X1    = 0x32
    ACC_IG_THS_Y1    = 0x33
    ACC_IG_THS_Z1    = 0x34
    ACC_IG_DUR1      = 0x35
    ACC_IG_CFG2      = 0x36
    ACC_IG_SRC2      = 0x37
    ACC_IG_THS2      = 0x38
    ACC_IG_DUR2      = 0x39
    ACC_XL_REFERENCE = 0x3A
    ACC_XH_REFERENCE = 0x3B
    ACC_YL_REFERENCE = 0x3C
    ACC_YH_REFERENCE = 0x3D
    ACC_ZL_REFERENCE = 0x3E
    ACC_ZH_REFERENCE = 0x3F

    MAG_WHO_AM_I   = 0x0F
    MAG_CTRL_REG1  = 0x20
    MAG_CTRL_REG2  = 0x21
    MAG_CTRL_REG3  = 0x22
    MAG_CTRL_REG4  = 0x23
    MAG_CTRL_REG5  = 0x24
    MAG_STATUS_REG = 0x27
    MAG_OUT_X_L    = 0x28
    MAG_OUT_X_H    = 0x29
    MAG_OUT_Y_L    = 0x2A
    MAG_OUT_Y_H    = 0x2B
    MAG_OUT_Z_L    = 0x2C
    MAG_OUT_Z_H    = 0x2D
    MAG_TEMP_OUT_L = 0x2E
    MAG_TEMP_OUT_H = 0x2F
    MAG_INT_CFG    = 0x30
    MAG_INT_SRC    = 0x31
    MAG_INT_THS_L  = 0x32
    MAG_INT_THS_H  = 0x33

    MAG_SCALE_2=0x00 #full-scale is +/-2Gauss
    MAG_SCALE_4=0x20 #+/-4Gauss
    MAG_SCALE_8=0x40 #+/-8Gauss
    MAG_SCALE_12=0x60 #+/-12Gauss

    ACCELE_SCALE=2

    ACC_ODR_50_Hz       = 0x20

    X=0
    Y=1
    Z=2

    # Set up the sensor
    def __init__(self,):
        self.write_acc_reg(self.ACC_ODR_50_Hz, self.ACC_CTRL1)	# turn it on and set the speed
        time.sleep(.005)

	# get the status of the sensor
    def status(self):
        if self.read_acc_reg(self.WHO_AM_I) != 0x41:
            return -1
        if self.read_mag_reg(self.WHO_AM_I) != 0x3D:
            return -1
        return 1

	# Write data to a reg on the I2C device
    def write_reg(self,data,reg):
        bus.write_byte_data(self.LSM303D_ADDR, reg, data)

    def write_acc_reg(self,data,reg):
        bus.write_byte_data(self.ACC_ADDR, reg, data)

    def write_mag_reg(self,data,reg):
        bus.write_byte_data(self.MAG_ADDR, reg, data)

	# Read data from the sensor
    def read_reg(self,reg):
        return bus.read_byte_data(self.LSM303D_ADDR, reg)

    def read_acc_reg(self,reg):
        return bus.read_byte_data(self.ACC_ADDR, reg)

    def read_mag_reg(self,reg):
        return bus.read_byte_data(self.MAG_ADDR, reg)

	# Check if compass is ready
    def isMagReady(self):
        if self.read_mag_reg(self.STATUS_REG_M)&0x03!=0:
            return 1
        return 0

	# Get raw accelerometer values
    def getAccel(self):
        raw_accel=[0,0,0]
        raw_accel[0]=(self.read_acc_reg(self.ACC_OUT_X_H)<<8)|self.read_acc_reg(self.ACC_OUT_X_L)
        raw_accel[1]=(self.read_acc_reg(self.ACC_OUT_Y_H)<<8)|self.read_acc_reg(self.ACC_OUT_Y_L)
        raw_accel[2]=(self.read_acc_reg(self.ACC_OUT_Z_H)<<8)|self.read_acc_reg(self.ACC_OUT_Z_L)

		#2's compiment
        for i in range(3):
            if raw_accel[i]>32767:
                raw_accel[i]=raw_accel[i]-65536

        return raw_accel

	# Get accelerometer values in g
    def getRealAccel(self):
        realAccel=[0.0,0.0,0.0]
        accel=self.getAccel()
        for i in range(3):
            realAccel[i] =round(accel[i] / math.pow(2, 15) * self.ACCELE_SCALE,3)
        return realAccel

	# Get compass raw values
    def getMag(self):
        raw_mag=[0,0,0]
        raw_mag[0]=(self.read_mag_reg(self.MAG_OUT_X_H)<<8)|self.read_mag_reg(self.MAG_OUT_X_L)
        raw_mag[1]=(self.read_mag_reg(self.MAG_OUT_Y_H)<<8)|self.read_mag_reg(self.MAG_OUT_Y_L)
        raw_mag[2]=(self.read_mag_reg(self.MAG_OUT_Z_H)<<8)|self.read_mag_reg(self.MAG_OUT_Z_L)

		#2's compiment
        for i in range(3):
            if raw_mag[i]>32767:
                raw_mag[i]=raw_mag[i]-65536

        return raw_mag

	# Get heading from the compass
    def getHeading(self):
        magValue = self.getMag()
        heading = 180*math.atan2(magValue[self.Y], magValue[self.X])/math.pi#  // assume pitch, roll are 0

        if (heading <0):
            heading += 360

        return round(heading,3)


    def getTiltHeading(self):
        magValue = self.getMag()
        accelValue = self.getRealAccel()

        X = self.X
        Y = self.Y
        Z = self.Z

        pitch = math.asin(-accelValue[X])

        print(accelValue[Y],pitch,math.cos(pitch),accelValue[Y]/math.cos(pitch),math.asin(accelValue[Y]/math.cos(pitch)))
        roll = math.asin(accelValue[Y]/math.cos(pitch))

        xh = magValue[X] * math.cos(pitch) + magValue[Z] * math.sin(pitch)
        yh = magValue[X] * math.sin(roll) * math.sin(pitch) + magValue[Y] * math.cos(roll) - magValue[Z] * math.sin(roll) * math.cos(pitch)
        zh = -magValue[X] * (roll) * math.sin(pitch) + magValue[Y] * math.sin(roll) + magValue[Z] * math.cos(roll) * math.cos(pitch)
        heading = 180 * math.atan2(yh, xh)/math.pi

        if (yh >= 0):
            return heading
        else:
            return (360 + heading)


if __name__ == "__main__":
    acc_mag=lsm303d()
    while True:
        print(acc_mag.getRealAccel())

        while True:
            if acc_mag.isMagReady():
                break
            print(acc_mag.getHeading())

		# Do not use, math error
		# print acc_mag.getTiltHeading()
