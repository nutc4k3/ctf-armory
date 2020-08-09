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


CMD_CLEAR_DISPLAY = 0x01
CMD_RETURN_HOME = 0x02
CMD_ENTRY_MODE_SET = 0x04
CMD_DISPLAY_CONTROL = 0x08
CMD_CURSOR_SHIFT = 0x10
CMD_FUNCTION_SET = 0x20
CMD_SET_CGRAM_ADDR = 0x40
CMD_SET_DDRAM_ADDR = 0x80

commands_desc = {
    CMD_CLEAR_DISPLAY: "Clear Display",
    CMD_RETURN_HOME: "Return Home",
    CMD_ENTRY_MODE_SET: "Entry Mode Set",
    CMD_DISPLAY_CONTROL: "Display Control",
    CMD_CURSOR_SHIFT: "Cursor Shift",
    CMD_FUNCTION_SET: "Function Set",
    CMD_SET_CGRAM_ADDR: "Set cgram address",
    CMD_SET_DDRAM_ADDR: "Set ddram address",
}

command_list = [
    # From higher to lower
    CMD_SET_DDRAM_ADDR,
    CMD_SET_CGRAM_ADDR,
    CMD_FUNCTION_SET,
    CMD_CURSOR_SHIFT,
    CMD_DISPLAY_CONTROL,
    CMD_ENTRY_MODE_SET,
    CMD_RETURN_HOME,
    CMD_CLEAR_DISPLAY,
]

def get_cmd(opcode):
    got_cmd = 0x00
    for idx in range(len(command_list)):
        cmd = command_list[idx]
        if opcode & cmd == cmd:
            got_cmd = cmd
            break
    return got_cmd

def get_cmd_description(opcode):
    got_cmd = get_cmd(opcode)
    if got_cmd == 0:
        return "CMD 0x%02x" % opcode

    cmd_str = commands_desc[got_cmd]
    if got_cmd == CMD_SET_DDRAM_ADDR:
        addr = opcode & ~(got_cmd)
        cmd_str += " 0x%02x" % addr
    elif got_cmd == CMD_SET_CGRAM_ADDR:
        addr = opcode & ~(got_cmd)
        cmd_str += " 0x%02x" % addr
    return cmd_str

class Decoder(srd.Decoder):
    api_version = 3
    id = 'hd44780'
    name = 'HD44780'
    longname = 'HD44780 LCD'
    desc = 'A HD44780 LCD Decoder'
    license = 'gplv2+'
    inputs = ['logic']
    outputs = []
    tags = ['LCD']
    options = ()
    annotations = (
        ('text', 'Text'),                               # 0
        ('warning', 'Warning'),                         # 1
        ('data-write-nibble', 'Data nibble write'),     # 2
        ('cmd-write-nibble', 'Command nibble write'),   # 3
        ('data-write', 'Data write'),                   # 4
        ('cmd-write', 'Command write'),                 # 5
        ('lcd_rs', 'LCD Command / Data'),               # 6
        ('lcd_en', 'LCD Enable'),                       # 7
        ('lcd_rw', 'LCD Read / Write'),                 # 8
    )
    annotation_rows = (
         ('lcd-rs', 'RS', (6,)),
         ('lcd-en', 'Enable', (7,)),
         ('lcd-rw', 'R/W', (8,)),
         ('data-write-nibble', 'Write Nibble', (2, 3)),
         ('write', 'Write', (4,5)),
    )
    binary = (
        ('data-read', 'Data read'),
        ('data-write', 'Data write'),
    )
    options = (
        {'id': 'lcd_mode', 'desc': 'LCD Mode',
            'default': '4bit', 'values': ('4bit', '8bit')},
    )

    def __init__(self):
        self.reset()

    def reset(self):
        self.state = 'IDLE'
        self.nibble_start = 0
        self.nibbles = [0x0, 0x0]
        self.current_nibble = 0

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

    def report_nibble(self, ss, es, is_cmd, nibble, data):
        self.put(ss, es, self.out_ann, [2 if not is_cmd else 3, ["NIBBLE %d = 0x%x" % (nibble, data)]])

    def report_rs(self, ss, es, lcd_rs):
        self.put(ss, es, self.out_ann, [6, ["CMD" if lcd_rs == 0 else "DATA"]])

    def report_en(self, ss, es, lcd_en):
        self.put(ss, es, self.out_ann, [7, ["%d" % (lcd_en)]])

    def report_rw(self, ss, es, lcd_rw):
        self.put(ss, es, self.out_ann, [8, ["READ" if lcd_rw == 1 else "WRITE"]])

    def update_data(self):
        self.data = (self.nibbles[0] << 4) + self.nibbles[1]

    def to_byte(self, data):
        databyte = 0
        num_bits = len(data)
        for i in range(num_bits):
            bit = data[i][0]
            databyte += bit << (num_bits-1-i)
        return databyte

    def process_data(self):
        self.ss = self.data_start
        self.es = self.data_end
        if (self.data >= 0x20 and self.data <= 0x7E):
            # Printable characters
            self.putx([4, ["'%s'" % chr(self.data)]])
        elif (self.data == ord('\n')):
            # Line Break
            self.putx([4, ["\\n" % chr(self.data)]])
        else:
            self.putx([4, ["0x%02x" % self.data]])
        #print("HD44780: DATA 0x%02x" % self.data)

    def process_cmd(self):
        self.ss = self.data_start
        self.es = self.data_end
        self.putx([5, [get_cmd_description(self.data)]])
        #print("HD44780: CMD 0x%02x" % self.data)

    def process_enable_low(self, ss, es, lcd_rs, lcd_rw, lcd_e, lcd_data):
        self.nibbles[self.current_nibble] = lcd_data
        self.report_nibble(self.nibble_start, es, lcd_rs == 0, self.current_nibble, lcd_data)
        self.state = 'IDLE'
        self.current_nibble += 1
        if self.current_nibble == 2: # Last nibble, set the end and process
            self.current_nibble = 0
            self.data_end = es
            self.update_data()      # Update data
            if lcd_rs == 0:         # Command
                self.process_cmd()
            else:                   # Data
                self.process_data()

    def process4bit(self, ss, es, data):
        #print("HD44780(4B): ", data)
        # LCD: | RS | RW | E  | D0 | D1 | D2 | D3 | D4 | D5 | D6 | D7 |
        # IN:  | D7 | D6 | D5 | NC | NC | NC | NC | D0 | D1 | D2 | D3 |
        if len(data) < 8:
            print("ERROR")
            return

        # Received bits are MSB-First. So inverted related to DX notation
        lcd_rs      = data[0][0]
        lcd_rw      = data[1][0]
        lcd_e       = data[2][0]
        lcd_data    = self.to_byte([data[7], data[6], data[5], data[4]])

        self.report_rs(ss, es, lcd_rs)
        self.report_rw(ss, es, lcd_rw)
        self.report_en(ss, es, lcd_e)

        if lcd_e == 0: # The LCD Latches the data on lower edge
            if self.state == 'NIBBLE':
                self.process_enable_low(ss, es, lcd_rs, lcd_rw, lcd_e, lcd_data)
        else:
            self.nibble_start = ss
            if self.state == 'IDLE':
                if self.current_nibble == 0:
                    self.data_start = ss
                self.state = 'NIBBLE'

    def process8bit(self, ss, es, data):
        # TODO
        print("HD44780(8B): ", data)
        pass

    def decode(self, ss, es, data):
        if self.options['lcd_mode'] == '4bit':
            self.process4bit(ss, es, data)
        else:
            self.process8bit(ss, es, data)
