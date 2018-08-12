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

    def decode_cmd(self, rxtx, s):
        # TODO: Maybe write down all the instructions on a tuple and
        # iterate over it?
        if s.startswith('page'):
            self.put_text('Refresh {}'.format(s))
            self.put_instruction('Refresh Page')
        elif s.startwith('ref'):
            self.put_text('Refresh component {}'.format(s))
            self.put_instruction('Refresh component')
    
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
        pdata = pdata[0]

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
