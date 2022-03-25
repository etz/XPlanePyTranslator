import socket
import struct

#socket information
localIP = "127.0.0.1"
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

#Listen for incoming datagram
while(True):
    bytesAddressPair = UDPServer.recvfrom(bufferSize)
    #convert to hex
    message = bytesAddressPair[0].hex()
    print("Raw Message: {}".format(message))
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
            data_values.append(value)
            #remove bytes from string
            message = message[8:]


        #print results to screen,reset values
        data_output.append(data_values)
        print(data_values)
        data_values = []

        #after translation of first datapoint, loop to next
        index_total = index_total - 1

    #convert keys and values to a dictionary
    data_dict = dict(zip(keys, zip(*data_output)))
    #reset keys and data_output
    keys = []
    data_output = []


    print(data_dict)
