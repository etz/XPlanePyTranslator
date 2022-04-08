import socket
from datetime import datetime
import time
import struct

#create a dictionary
keys = []
data_output = []
data_dict = {}

#socket information
localIP = "127.0.0.1"
localPort = 20001
bufferSize = 1024

#Create a datagram socket
UDPServer = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
c_time = datetime.now().strftime("%m-%d-%y-%H-%M")
flight_file = "flight-" + c_time
f = open(flight_file, "w")


UDPServer.bind((localIP,localPort))

print("UDP Server Listening...")

#Listen for incoming datagram
while(True):
    bytesAddressPair = UDPServer.recvfrom(bufferSize)
    #convert to hex
    message = bytesAddressPair[0].hex()
    f.write("{}\n".format(message))
    f.flush()

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
    print(data_dict)
    #reset keys and data_output
    keys = []
    data_output = []
    #print("Hex Message: {}".format(message))
