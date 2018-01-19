"""
'shift_in_out_demo.py'.

=================================================
shifts data into and out of a data pin
"""

import time
import board
import digitalio
import simpleio

# set up clock, data, and latch pins
CLK = digitalio.DigitalInOut(board.D12)
CLK.direction = digitalio.Direction.OUTPUT
DATA = digitalio.DigitalInOut(board.D11)
LATCH = digitalio.DigitalInOut(board.D10)
LATCH.direction = digitalio.Direction.OUTPUT

while True:
    DATA_TO_SEND = 256
    # shifting 256 bits out of DATA pin
    LATCH.value = False
    DATA.direction = digitalio.Direction.OUTPUT
    print('shifting out...')
    simpleio.shift_out(DATA, CLK, DATA_TO_SEND, msb_first=False)
    LATCH.value = True
    time.sleep(3)

    # shifting 256 bits into the DATA pin
    LATCH.value = False
    DATA.direction = digitalio.Direction.INPUT
    print('shifting in...')
    simpleio.shift_in(DATA, CLK)
    time.sleep(3)
