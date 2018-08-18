##
## This file is part of the libsigrokdecode project.
##
## Copyright (C) 2018 Carlos Diaz <github.com/C47D>
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

# https://sigrok.org/wiki/Protocol_decoder_API

# Nextion instruction set taken from
# https://www.itead.cc/wiki/Nextion_Instruction_Set


class Decoder(srd.Decoder):
    api_version = 3
    id = 'nextion'
    name = 'Nextion'
    longname = 'Decoder for Nextion displays instruction set'
    desc = 'Decoder for Nextion displays instruction set'
    license = 'gplv2+'
    inputs = ['uart']
    outputs = ['nextion']
    annotations = (
        ('instruction', 'Nextion instruction'),
        ('text', 'Human readable text'),
        ('warning', 'Warnings')
    )

    def __init__(self):
        self.reset()

    def reset(self):
        # [] es una lista
        self.cmd = ['', '']
        self.ss_block = None

    def start(self):
        # This function is called before the beginning of the decoding
        # This is the place to register() the output types, check the
        # user-supplied PD options for validity, and so on.

        self.out_ann = self.register(srd.OUTPUT_ANN)

    def putp(self, msg):
        # data parameters content depend on the output type:
        # - OUTPUT_ANN: The data parameter is a Python list with
        # two items. The first item is the annotation index, the
        # second is a list of annotation strings. The strings should
        # be longer and shorter versions of the same annotation text
        # (sorted by length, longest first), which can be used by
        # frontends to show different annotation texts depending on
        # e.g. zoom level.
        # Example: self.put(10, 20, self.out_ann, [4, ['Start', 'St', 'S']])
        # The emmited data spans samples 10 to 20, is of type OUTPUT_ANN
        # the annotation index is 4, the list of annotations strings
        # is "Start", "St" and "S".
        self.put(self.ss_block, self.es_block, self.out_ann, msg)

    def put_instruction(self, msg):
        self.put(self.ss_block, self.es_block, self.out_ann, [0, [msg]])

    def put_text(self, msg):
        self.put(self.ss_block, self.es_block, self.out_ann, [1, [msg]])

    def char_to_int(self, number):
        return int(ord(number))

    def decode_cmd(self, rxtx, s):
        # Decode TX data
        if rxtx == 1:
            print('Decoding tx data {}'.format(s.encode()))
            if s.startswith('page'):
                self.put_text('Refresh {}'.format(s))
                self.put_instruction('Refresh Page')
            elif s.startswith('ref'):
                self.put_text('Refresh component {}'.format(s))
                self.put_instruction('Refresh component')
        elif rxtx == 0: # Decode RX data
            if s == chr(0x00):
                self.put_text('Invalid instruction')
                self.put_instruction('Invalid instruction')
            elif s == chr(0x01):
                self.put_text('Successful execution')
                self.put_instruction('Successful execution')
            elif s == chr(0x02):
                self.put_text('Component ID invalid')
                self.put_instruction('Component ID invalid')
            elif s == chr(0x03):
                self.put_text('Page ID invalid')
                self.put_instruction('Page ID invalid')
            elif s == chr(0x04):
                self.put_text('Picture ID invalid')
                self.put_instruction('Picture ID invalid')
            elif s == chr(0x05):
                self.put_text('Font execution')
                self.put_instruction('Font execution')
            elif s == chr(0x11):
                self.put_text('Baudrate setting invalid')
                self.put_instruction('Baudrate setting invalid')
            elif s == chr(0x12):
                self.put_text('Curve control ID number or channel invalid')
                self.put_instruction('Curve control ID number or channel invalid')
            elif s == chr(0x1A):
                self.put_text('Variable name invalid')
                self.put_instruction('Variable name invalid')
            elif s == chr(0x1B):
                self.put_text('Variable operation invalid')
                self.put_instruction('Variable operation invalid')
            elif s == chr(0x1C):
                self.put_text('Failed to assign')
                self.put_instruction('Failed to assign')
            elif s == chr(0x1D):
                self.put_text('Operate EEPROM failed')
                self.put_instruction('Operate EEPROM failed')
            elif s == chr(0x1E):
                self.put_text('Parameter quantity invalid')
                self.put_instruction('Parameter quantity invalid')
            elif s == chr(0x1F):
                self.put_text('IO operation invalid')
                self.put_instruction('IO operation invalid')
            elif s == chr(0x20):
                self.put_text('Undefined escape characters')
                self.put_instruction('Undefined escape characters')
            elif s == chr(0x23):
                self.put_text('Too long variable name')
                self.put_instruction('Too long variable name')
            elif s == chr(0x86):
                self.put_text('Device automatically enters into sleep mode')
                self.put_instruction('Device automatically enters into sleep mode')
            elif s == chr(0x87):
                self.put_text('Device automatically wake up')
                self.put_instruction('Device automatically wake up')
            elif s == chr(0x88):
                self.put_text('System successful start up')
                self.put_instruction('System successful start up')
            elif s == chr(0x89):
                self.put_text('Start SD upgrade')
                self.put_instruction('Start SD upgrade')
            elif s == chr(0xFD):
                self.put_text('Data transparent transmit finished')
                self.put_instruction('Data transparent transmit finished')
            elif s == chr(0xFE):
                self.put_text('Data transparent transmit ready')
                self.put_instruction('Data transparent transmit ready')
            # Begin of return codes with multiple bytes
            elif s[0] == chr(0x65): # touch event return data
                # 0x65 + Page ID + Component ID + TouchEvent + End
                # TouchEvent: Press event = 0x01, Release Event = 0x00
                event = self.char_to_int(s[-1])
                page_id = self.char_to_int(s[1])
                component_id = self.char_to_int(s[2])
                if event == 1:
                    touch_event = 'Press'
                elif event == 0:
                    touch_event = 'Release'
                else:
                    touch_event = 'Invalid'
                self.put_text('Page ID: {}, Component: ID {}, {} event'.format(page_id, component_id, touch_event))
                self.put_instruction('Touch event return data')
            elif s[0] == chr(0x66): # current page id number returns
                # 0x66 + Page ID + End
                page_id = self.char_to_int(s[1])
                self.put_text('Current Page ID: {}'.format(page_id))
                self.put_instruction('Current page ID number returns')
            elif s[0] == chr(0x67): # touch coordinate data returns
                # 0x67 + Coordinate X High-order + Coordinate X Low + Coordinate Y High + Coordinate Y Low + TouchEvent State
                # TouchEvent: Press Event 0x01, Release Event 0x00
                # 0x67 0x00 0x7A 0x00 0x1E 0x01 0xFF 0xFF 0xFF
                # Meaning: Coordinate(122, 30) Press event
                x_high = self.char_to_int(s[1])
                x_low = self.char_to_int(s[2])
                y_high = self.char_to_int(s[3])
                y_low = self.char_to_int(s[4])
                event = self.char_to_int(s[-1])
                
                x_cord = x_high + x_low
                y_cord = y_high + y_low
                if event == 1:
                    touch_event = 'Press'
                elif event == 0:
                    touch_event = 'Release'
                else:
                    touch_event = 'Invalid'
                self.put_text('Coordinate ({}, {}), {} event'.format(x_cord, y_cord, touch_event))
                self.put_instruction('Touch coordinate data returns')
            elif s[0] == chr(0x68): # touch event in sleep mode
                # 0x68 + Coordinate X High-order + Coordinate X Low + Coordinate Y High + Coordinate Y Low + TouchEvent State
                # TouchEvent: Press Event 0x01, Release Event 0x00
                # 0x68 0x00 0x7A 0x00 0x1E 0x01 0xFF 0xFF 0xFF
                # Meaning: Coordinate(122, 30) Press event
                x_high = self.char_to_int(s[1])
                x_low = self.char_to_int(s[2])
                y_high = self.char_to_int(s[3])
                y_low = self.char_to_int(s[4])
                event = self.char_to_int(s[-1])

                x_cord = x_high + x_low
                y_cord = y_high + y_low
                if event == 1:
                    touch_event = 'Press'
                elif event == 0:
                    touch_event = 'Release'
                else:
                    touch_event = 'Invalid'
                self.put_text('Coordinate ({}, {}), {} event'.format(x_cord, y_cord, touch_event))
                self.put_instruction('Touch coordinate data returns')
                self.put_text('Touch event in sleep mode')
                self.put_instruction('Touch event in sleep mode')
            elif s[0] == chr(0x70): # string variable data returns
                # 0x70 string variable data returns
                # 0x70 + Variable Content in ASCII code + End
                # 0x70 0x61 0x62 0x63 0xFF 0xFF 0xFF
                # Meaning: return value data: "abc"

                # TODO
                
                self.put_text('String variable data returns: {}'.format(return_str))
                self.put_instruction('String variable data returns')
            elif s[0] == chr(0x71): # numeric variable data returns
                # 0x71 numeric variable data returns
                # 0x71 + Variable binary data (4 bytes little endian, low in front) + End
                # 0x71 0x66 0x00 0x00 0x00 0xFF 0xFF 0xFF
                # Meaning: return value data: 102
                value = s[1] + s[2] + s[3] + s[4]
                self.put_text('Numeric variable data returns')
                self.put_instruction('Numeric variable data returns')
            
    def decode(self, start_sample, end_sample, data):
        '''
        OUTPUT_PYTHON format: (from uart decoder)
        Packet:
        [<ptype>, <rxtx>, <pdata>]
        This is the list of <ptype>s and their respective <pdata> values:
         - 'STARTBIT': The data is the (integer) value of the start bit (0/1).
         - 'DATA': This is always a tuple containing two items:
           - 1st item: the (integer) value of the UART data. Valid values
             range from 0 to 511 (as the data can be up to 9 bits in size).
           - 2nd item: the list of individual data bits and their ss/es numbers.
         - 'PARITYBIT': The data is the (integer) value of the parity bit (0/1).
         - 'STOPBIT': The data is the (integer) value of the stop bit (0 or 1).
         - 'INVALID STARTBIT': The data is the (integer) value of the start bit (0/1).
         - 'INVALID STOPBIT': The data is the (integer) value of the stop bit (0/1).
         - 'PARITY ERROR': The data is a tuple with two entries. The first one is
           the expected parity value, the second is the actual parity value.
         - TODO: Frame error?
        The <rxtx> field is 0 for RX packets, 1 for TX packets.
        '''
        
        ptype, rxtx, pdata = data

        # for now ignore all UART packets except the actual data packets
        if ptype != 'DATA':
            return

        # We're only interested in the byte value (see DATA above)
        pdata = pdata[0] # RX packets

        # If this is the start of a command/reply, remember the start sample.
        if self.cmd[rxtx] == '':
            self.ss_block = start_sample

        # Append a new (ASCII) byte to the currently parsed command
        self.cmd[rxtx] += chr(pdata)

        # Get bytes until a END_OF_CMD (ÿÿÿ) sequence is found
        if self.cmd[rxtx][-3:] != 'ÿÿÿ':
           return

        # Handle host commands and device replies
        # We remove trailing ÿÿÿ from the string before handling them
        self.es_block = end_sample

        # decode data
        self.decode_cmd(rxtx, self.cmd[rxtx][:-3])

        self.cmd[rxtx] = ''
