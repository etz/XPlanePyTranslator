import socket
import time
import binascii

f = open("flight-03-11-22-10-34", "r")
lines = f.readlines()
increment = 0

ip = "127.0.0.1"
port = "49000"

UDPServer = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)


while True:
    line = binascii.unhexlify(lines[increment][:-1])
    UDPServer.sendto(line, (ip, int(port)))
    time.sleep(0.1)
    increment = increment + 1
