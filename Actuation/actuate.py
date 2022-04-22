#!/usr/bin/python

#actuate the RV E-flite 1.7m based on X-Plane data.
#debugging on non-pi? comment out 'pwm.', 'pwm =' statements and import smbus

import time
import math
import smbus
import socket
import struct
import logging

#logging level
#DEBUG - print translated data and actuation PWM, most verbose
#INFO - show actuation PWM, less verbose
#WARNING - default, no verbosity
logging.basicConfig(level=logging.DEBUG)


#socket information
localIP = "127.0.0.1" #local ipv4 address
localPort = 20001 #listening port
bufferSize = 1024




keys = [] #the numbers associated with the General Data Outputs extracted from x-plane
data_output = [] #stores values from each General Data Outputs
data_dict = {} #allows for the interpretation of specific General Data Outputs from X-Plane ex. data_dict[key][0]

#Create a socket where we will listen for X-Plane data
UDPServer = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServer.bind((localIP,localPort))

logging.warning("UDP Server Listening...")

# ============================================================================
# Raspi PCA9685 16-Channel PWM Servo Driver (from Waveshare: https://www.waveshare.com/wiki/Servo_Driver_HAT)
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


if __name__=='__main__':

    #enable the actuation
    #pwm = PCA9685(0x40, debug=False)
    pwm.setPWMFreq(50)

    while True:
        # PACKET TRANSLATION - convert UDP bytes to index values, floats and store in data_dict

        bytesAddressPair = UDPServer.recvfrom(bufferSize) #wait for incoming transmission
        message = bytesAddressPair[0].hex() #convert byte-encoded packet to hex
        #logging.debug("Raw Message: {}".format(message)) #uncomment to print raw bytes

        message = message[10:] #remove DATA* before interpretation

        if(len(message)%72 != 0):
            """Close the program if malformed packets are received"""
            logging.critical("Incorrect packet size")
            quit()

        index_total = len(message)/72 #determine number of datapoints to translate

        while index_total != 0:
            """store the General Data Outputs index, translate each datapoint (36 bytes each), append to data_output"""
            keys.append(int(message[:2], 16)) #parse General Data Outputs index
            message = message[8:] #remove the 8 bytes that store the index number

            data_values = [] #list that will store the translated x-plane values

            for x in range(8):
                """Convert each precision floating point value (up to 8) from bytes and store in data_values"""
                value = struct.unpack('f', bytes.fromhex(message[:8]))[0]
                data_values.append(round(value,4)) #round the value as it can move up or down easily
                message = message[8:] #remove bytes from string

            data_output.append(data_values)
            data_values = []

            index_total = index_total - 1 #iterate through each key until complete


        data_dict = dict(zip(keys, tuple(data_output))) #convert keys and values to a dictionary
        logging.debug("{}".format(data_dict))

        keys = [] #reset keys and data_output for next packet
        data_output = []


        #CONSTANTS -- extract plane datapoints to variables
        throttle = data_dict[25][0] #throttle data
        logging.debug("Throttle Data: {}".format(throttle))

        #elevator data
        elevator = data_dict[11][0]
        elevator_norm = (elevator--1)/(1--1)
        logging.debug("Elevator Data: {}, {} (normalized)".format(elevator,elevator_norm))

        #aileron data (normalized between 0-1)
        aileron = data_dict[11][1]
        aileron_norm = (aileron--1)/(1--1)
        logging.debug("Aileron Data: {}, {} (normalized)".format(aileron,aileron_norm))

        #rudder data
        rudder = data_dict[11][2]
        rudder_norm = (rudder--0.1950)/(0.2050--0.1950)
        logging.debug("Rudder Data: {}, {} (normalized)".format(rudder,rudder_norm))

        #flaps data
        flaps = data_dict[13][3]
        logging.debug("Flaps Data: {}".format(flaps))




        #ACTUATE - move servos based on input

        if throttle > 0: #actuate throttle
            speed = (2000*throttle)+500
            pwm.setServoPulse(10,speed)
            logging.info("Throttle PWM: {}".format(speed))
            time.sleep(0.02)

        if elevator_norm != 0.5: #actuate elevator
            elevator = (2000*aileron_norm)+500
            reverse = 2500-elevator
            elevator = 500+reverse
            pwm.setServoPulse(2,elevator)
            logging.info("Elevator PWM: {}".format(elevator))
            time.sleep(0.02)
        else:
            pwm.setServoPulse(2,1500)
            pass

        if aileron_norm != 0.5: #actuate ailerons
            ailerons = (2000*aileron_norm)+500
            reverse = 2500-ailerons
            ailerons = 500+reverse
            pwm.setServoPulse(4,ailerons)
            logging.info("Aileron PWM: {}".format(ailerons))
            time.sleep(0.02)
        else:
            pwm.setServoPulse(4,1500)
            pass

        if rudder_norm != 0.5: #actuate rudder
            rudder = (2000*rudder_norm)+500
            pwm.setServoPulse(6,rudder)
            logging.info("Rudder PWM: {}".format(rudder))
            time.sleep(0.02)
        else:
            pwm.setServoPulse(6,1500)
            pass

        if flaps != 0: #actuate flaps
            flaps = 2500-(flaps*2000)
            pwm.setServoPulse(8,flaps)
            logging.info("Flap PWM: {}".format(flaps))
            time.sleep(0.02)
        else:
            pwm.setServoPulse(8,2500)
            pass
