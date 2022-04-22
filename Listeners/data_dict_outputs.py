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
while True:

        # PACKET TRANSLATION - convert UDP bytes to index values, floats and store in data_dict

    bytesAddressPair = UDPServer.recvfrom(bufferSize)  # wait for incoming transmission
    message = bytesAddressPair[0].hex()  # convert byte-encoded packet to hex

        # logging.debug("Raw Message: {}".format(message)) #uncomment to print raw bytes

    message = message[10:]  # remove DATA* before interpretation

    if len(message) % 72 != 0:
        logging.critical('Incorrect packet size')
        quit()

    index_total = len(message) / 72  # determine number of datapoints to translate

    while index_total != 0:
        key = int(message[:2], 16)
        #keys.append(int(message[:2], 16))  # parse General Data Outputs index
        message = message[8:]  # remove the 8 bytes that store the index number

        data_values = []  # list that will store the translated x-plane values

        for x in range(8):
            value = struct.unpack('f', bytes.fromhex(message[:8]))[0]
            data_values.append(value)  # round the value as it can move up or down easily
            message = message[8:]  # remove bytes from string

        data_dict[key] = data_values
        data_values = []

        index_total = index_total - 1  # iterate through each key until complete

    #data_dict = dict(zip(keys, tuple(data_output)))  # convert keys and values to a dictionary
    #logging.debug('{}'.format(data_dict))

    #keys = []  # reset keys and data_output for next packet
    #data_output = []

    print(data_dict)
