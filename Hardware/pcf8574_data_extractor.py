''' 
Parses only the data of the PCF8574 communication from an analysed i2c file (saleae output, for example)
'''

import csv
import sys
import binascii

file = sys.argv[1]

PCF_RS = 0x01
PCF_EN = 0x04

packets = []
with open(file,'r') as f:
	next(f)
	for i in f:
		x = i.split(',')
		packets.append(int(x[3],16))

data_packets = []
for packet in packets:
	if (packet&PCF_RS) and (packet&PCF_EN):
		data_packets.append(packet)

print(data_packets)
for i in range(0, len(data_packets), 2):
	higher = data_packets[i]
	lower = data_packets[i+1]
	print(chr((higher&0xF0)|(lower>>4)), end='')

'''
To-do:

Make it work with sigrok!

import subprocess
import os
import sys

sigrok_dir = os.getenv('sigrok-cli')
sigrok_cmd = 'sigrok-cli -i' + sys.argv[1] '-P i2c:scl=D1:sda=D0:address_format=unshifted -A i2c=address-read:address-write:data-read:data-write'

os.chdir(sigrok_dir) # set working dir to sigrok_dir
output = subprocess.run(sigrok_cmd, shell=True, check=True, capture_output=True, text=True) # open a new process, send the command and return the data
raw_data = output.stdout
'''
