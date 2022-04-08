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
    message = bytesAddressPair[0]
    print("Raw Message: {}".format(message))
