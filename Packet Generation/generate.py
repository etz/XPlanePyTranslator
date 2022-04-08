import struct
import binascii
import ast


data_dict = input("Enter the data_dict to be converted to a packet:\n")
data_dict = ast.literal_eval(data_dict)
message = "444154412a" #DATA:
keys = list(data_dict.keys())

#convert data_dict to hex
for key in keys:
    message = message + hex(key)[2:] #add key
    for value in data_dict[key]:
        message = message + value.hex()[2:]

print(message)
