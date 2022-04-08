#!/usr/bin/python

import time
import math
import smbus
import socket
import struct

#socket information
localIP = "192.168.0.15"
localPort = 20001
bufferSize = 1024

#create a dictionary
keys = []
data_output = []
data_dict = {}

#Create a datagram socket
UDPServer = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

UDPServer.bind((localIP,localPort))

print("UDP Server Listening...")

# ============================================================================
# Raspi PCA9685 16-Channel PWM Servo Driver
# ============================================================================

class PCA9685:

  # Registers/etc.
    __SUBADR1            = 0x02
    __SUBADR2            = 0x03
    __SUBADR3            = 0x04
    __MODE1              = 0x00
    __PRESCALE           = 0xFE
    __LED0_ON_L          = 0x06
    __LED0_ON_H          = 0x07
    __LED0_OFF_L         = 0x08
    __LED0_OFF_H         = 0x09
    __ALLLED_ON_L        = 0xFA
    __ALLLED_ON_H        = 0xFB
    __ALLLED_OFF_L       = 0xFC
    __ALLLED_OFF_H       = 0xFD

    def __init__(self, address=0x40, debug=False):
        self.bus = smbus.SMBus(1)
        self.address = address
        self.debug = debug
        if (self.debug):
            print("Reseting PCA9685")
        self.write(self.__MODE1, 0x00)

    def write(self, reg, value):
        "Writes an 8-bit value to the specified register/address"
        self.bus.write_byte_data(self.address, reg, value)
        if (self.debug):
            print("I2C: Write 0x%02X to register 0x%02X" % (value, reg))

    def read(self, reg):
        "Read an unsigned byte from the I2C device"
        result = self.bus.read_byte_data(self.address, reg)
        if (self.debug):
            print("I2C: Device 0x%02X returned 0x%02X from reg 0x%02X" % (self.address, result & 0xFF, reg))
        return result

    def setPWMFreq(self, freq):
        "Sets the PWM frequency"
        prescaleval = 25000000.0    # 25MHz
        prescaleval /= 4096.0       # 12-bit
        prescaleval /= float(freq)
        prescaleval -= 1.0
        if (self.debug):
            print("Setting PWM frequency to %d Hz" % freq)
            print("Estimated pre-scale: %d" % prescaleval)
        prescale = math.floor(prescaleval + 0.5)
        if (self.debug):
            print("Final pre-scale: %d" % prescale)

        oldmode = self.read(self.__MODE1);
        newmode = (oldmode & 0x7F) | 0x10        # sleep
        self.write(self.__MODE1, newmode)        # go to sleep
        self.write(self.__PRESCALE, int(math.floor(prescale)))
        self.write(self.__MODE1, oldmode)
        time.sleep(0.005)
        self.write(self.__MODE1, oldmode | 0x80)

    def setPWM(self, channel, on, off):
        "Sets a single PWM channel"
        self.write(self.__LED0_ON_L+4*channel, on & 0xFF)
        self.write(self.__LED0_ON_H+4*channel, on >> 8)
        self.write(self.__LED0_OFF_L+4*channel, off & 0xFF)
        self.write(self.__LED0_OFF_H+4*channel, off >> 8)
        if (self.debug):
            print("channel: %d  LED_ON: %d LED_OFF: %d" % (channel,on,off))

    def setServoPulse(self, channel, pulse):
        "Sets the Servo Pulse,The PWM frequency must be 50HZ"
        pulse = pulse*4096/20000        #PWM frequency is 50HZ,the period is 20000us
        self.setPWM(channel, 0, int(pulse))

def normalize(val, Rmin, max):
    normalized = (val-min)/(max-min)
    return normalized


if __name__=='__main__':

    pwm = PCA9685(0x40, debug=False)
    pwm.setPWMFreq(50)
    while True:
        #wait for incoming transmission
        bytesAddressPair = UDPServer.recvfrom(bufferSize)
        #convert to hex
        message = bytesAddressPair[0].hex()

        #print raw message (debug)
        #print("Raw Message: {}".format(message))

        #remove DATA*
        message = message[10:]

        if(len(message)%72 != 0):
            #Incorrect length
            print("Incorrect packet size")
            quit()

        #number of datapoints to translate
        index_total = len(message)/72

        #translate each datapoint (36 bytes each)
        while index_total != 0:
            #parse datapoint index number
            keys.append(int(message[:2], 16))
            #remove data_index bytes
            message = message[8:]

            #array for values
            data_values = []

            #convert each value, store in data_values
            for x in range(8):
                #convert first 4 bytes to precision floating point
                value = struct.unpack('f', bytes.fromhex(message[:8]))[0]
                data_values.append(round(value,4))
                #remove bytes from string
                message = message[8:]


            #print results to screen,reset values
            data_output.append(data_values)
            #print(data_values)
            data_values = []

            #after translation of first datapoint, loop to next
            index_total = index_total - 1

        #convert keys and values to a dictionary
        data_dict = dict(zip(keys, tuple(data_output)))
        #reset keys and data_output
        keys = []
        data_output = []


        #CONSTANTS -- extract plane datapoints to variables

        #throttle data
        throttle = data_dict[25][0]
        #print(throttle)

        #elevator data
        elevator = data_dict[11][0]
        elev_norm = (ailrn--1)/(1--1)

        #ailrn data (normalized between 0-1)
        ailrn = data_dict[11][1]
        ailrn_norm = (ailrn--1)/(1--1)
        #print(ailrn_norm)

        #rudder data
        rudder = data_dict[11][2]
        rudder_norm = (rudder--0.1950)/(0.2050--0.1950)

        #flaps data
        flaps = data_dict[13][3]




        #ACTUATE - move servos based on input

        #throttle
        if throttle > 0:
            speed = (2000*throttle)+500
            print("speed= " + str(speed))
            pwm.setServoPulse(10,speed)
            time.sleep(0.02)

        #elevator -- spot #2 on HAT
        if elev_norm != 0.5:
            elevator = (2000*ailrn_norm)+500
            reverse = 2500-elevator
            #print("reverse= " + str(reverse))
            elevator = 500+reverse
            #print("elevator= " + str(elevator))
            pwm.setServoPulse(2,elevator)
            time.sleep(0.02)
        else:
            pwm.setServoPulse(2,1500)

        #ailerons -- spot #4 on HAT
        if ailrn_norm != 0.5:
            ailrns = (2000*ailrn_norm)+500
            reverse = 2500-ailrns
            #print("reverse= " + str(reverse))
            ailrns = 500+reverse
            #print("ailrns= " + str(ailrns))
            pwm.setServoPulse(4,ailrns)
            time.sleep(0.02)
        else:
            pwm.setServoPulse(4,1500)

        #rudder -- spot #6 on HAT
        if rudder_norm != 0.5:
            rudder = (2000*rudder_norm)+500
            #reverse = 2500-rudder
            #print("reverse= " + str(reverse))
            #rudder = 500+reverse
            #print("ailrns= " + str(ailrns))
            pwm.setServoPulse(6,rudder)
            time.sleep(0.02)
        else:
            pwm.setServoPulse(6,1500)

        #flaps -- spot #8 on HAT
        if flaps != 0:
            flaps = 2500-(flaps*2000)
            pwm.setServoPulse(8,ailrns)
            time.sleep(0.02)
        else:
            pwm.setServoPulse(8,2500)
