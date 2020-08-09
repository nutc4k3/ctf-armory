##
## This file is part of the libsigrokdecode project.
##
## Copyright (C) 2020 Lucas Teske <lucas@teske.com.br>
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, see <http://www.gnu.org/licenses/>.
##


import sigrokdecode as srd

pcfaddr = 0x27

class Decoder(srd.Decoder):
    api_version = 3
    id = 'pcf8574'
    name = 'PCF8574'
    longname = 'PCB8574 I2C I/O Extender'
    desc = 'I2C 8 Bit I/O extender.'
    license = 'gplv2+'
    inputs = ['i2c']
    outputs = ['logic']
    tags = ['IO']
    options = ()
    annotations = (
        ('text', 'Text'),
        ('warning', 'Warning'),
        ('data-read', 'Data read'),
        ('data-write', 'Data write'),
    )
    binary = (
        ('data-read', 'Data read'),
        ('data-write', 'Data write'),
    )

    def __init__(self):
        self.reset()

    def reset(self):
        self.state = 'IDLE'
        self.nextstate = 'IDLE'
        self.databytes = []
        self.addr = 0x00

    def start(self):
        self.out_ann = self.register(srd.OUTPUT_ANN)
        self.out_python = self.register(srd.OUTPUT_PYTHON)
        self.out_binary = self.register(srd.OUTPUT_BINARY)

    def putp(self, data):
        self.put(self.ss, self.es, self.out_python, data)

    def putx(self, data):
        self.put(self.ss, self.es, self.out_ann, data)

    def putb(self, data):
        self.put(self.ss, self.es, self.out_binary, data)

    def process_datawrite(self, ss, es, data):
      cmd, series = data
      self.state = 'IDLE'
      self.state = 'WAITACK'
      self.nextstate = 'IDLE'
      databyte = self.bits_to_byte(data)
      #print("Wrote data", hex(databyte))
      self.putx([3, ["Write 0x%02x" % databyte]])
      self.putb(databyte)
      self.putp(series)

    def process_dataread(self, ss, es, data):
      self.state = 'WAITACK'
      self.nextstate = 'IDLE'
      databyte = self.bits_to_byte(data)
      self.putx([3, ["Read 0x%02x" % databyte]])
      self.putb(databyte)
      #print("Read data", hex(databyte))

    def process_ack(self, ss, es, data):
      #print("ACK Received. Next state: %s" %self.nextstate)
      self.state = self.nextstate

    def bits_to_byte(self, data):
      cmd, series = data
      databyte = 0
      for i in range(len(series)):
        bit = series[i][0]
        databyte += bit << (7-i)
      return databyte

    def decode(self, ss, es, data):
      cmd, databyte = data

      # Store the start/end samples of this I²C packet.
      self.ss, self.es = ss, es

      #print("DEBUG(%s): %s" %(cmd, databyte))
      if self.state == 'IDLE':
        # print("CMD", cmd, ", ", databyte, "")
        if cmd == "ADDRESS WRITE" and databyte == pcfaddr:
            #print("ADDR WROTE ", hex(databyte))
            self.addr = databyte
            self.nextstate = 'DATAWRITE'
            self.state = 'WAITACK'
        if cmd == "ADDRESS READ" and databyte == pcfaddr:
          #print("ADDR READ ", hex(databyte))
          self.addr = databyte
          self.nextstate = 'DATAREAD'
          self.state = 'WAITACK'
      elif self.state == 'WAITACK' and cmd == 'ACK':
        self.process_ack(ss, es, data)
      elif self.state == 'DATAREAD':
        self.process_dataread(ss, es, data)
      elif self.state == 'DATAWRITE':
        self.process_datawrite(ss, es, data)
