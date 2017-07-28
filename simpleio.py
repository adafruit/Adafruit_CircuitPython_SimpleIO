# The MIT License (MIT)
#
# Copyright (c) 2017 Scott Shawcroft for Adafruit Industries.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`simpleio` - Simple, beginner friendly IO.
=================================================

.. module:: simpleio
  :synopsis: Simple, beginner friendly IO.
  :platform: SAMD21, ESP8266

The `simpleio` module contains classes to provide simple access to IO.
"""

import digitalio
import math
from neopixel_write import neopixel_write

class DigitalOut:
    """
    Simple digital output that is valid until soft reset.
    """
    def __init__(self, pin):
        self.io = digitalio.DigitalInOut(pin)
        self.io.switch_to_output()

    @property
    def value(self):
        """The digital logic level of the output pin."""
        return self.io.value

    @value.setter
    def value(self, value):
        self.io.value = value

class DigitalIn:
    """
    Simple digital input that is valid until soft reset.
    """
    def __init__(self, pin):
        self.io = digitalio.DigitalInOut(pin)
        self.io.switch_to_input()

    @property
    def value(self):
        """The digital logic level of the input pin."""
        return self.io.value

    @value.setter
    def value(self, value):
        raise AttributeError("Cannot set the value on a digital input.")

class NeoPixel:
    """
    A sequence of neopixels.

    :param ~microcontroller.Pin pin: The pinto output neopixel data on.
    :param int n: The number of neopixels in the chain
    :param bool rgbw: True if the neopixels are RGBW

    Example for Circuit Playground Express:

    .. code-block:: python

        import simpleio
        from board import *

        RED = 0x100000

        with simpleio.NeoPixel(NEOPIXEL, 10) as pixels:
            for i in len(pixels):
                pixels[i] = RED
    """
    def __init__(self, pin, n, rgbw=False):
        self.pin = digitalio.DigitalInOut(pin)
        self.pin.switch_to_output()
        self.bpp = 3
        if rgbw:
            self.bpp = 4
        self.buf = bytearray(n * self.bpp)

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        # Blank out the neopixels.
        for i in range(len(self.buf)):
            self.buf[i] = 0
        neopixel_write(self.pin, self.buf)
        self.pin.deinit()

    def __repr__(self):
        return "[" + ", ".join(["0x%06x" % (x,) for x in self]) + "]"

    def _set_item(self, index, value):
        offset = index * self.bpp
        r = value >> 16
        g = (value >> 8) & 0xff
        b = value & 0xff
        w = 0
        # If all components are the same and we have a white pixel then use it
        # instead of the individual components.
        if self.bpp == 4 and r == g and g == b:
            w = r
            r = 0
            g = 0
            b = 0
        self.buf[offset + 1] = r
        self.buf[offset] = g
        self.buf[offset + 2] = b
        if self.bpp == 4:
            self.buf[offset + 3] = w

    def __setitem__(self, index, val):
        if isinstance(index, slice):
            start, stop, step = index.indices(len(self.buf) // self.bpp)
            length = stop - start
            if step != 0:
                length = math.ceil(length / step)
            if len(val) != length:
                raise ValueError("Slice and input sequence size do not match.")
            for val_i, in_i in enumerate(range(start, stop, step)):
                self._set_item(in_i, val[val_i])
        else:
            self._set_item(index, val)

        neopixel_write(self.pin, self.buf)

    def __getitem__(self, index):
        if isinstance(index, slice):
            out = []
            for in_i in range(*index.indices(len(self.buf) // self.bpp)):
                out.append(self[in_i])
            return out
        offset = index * self.bpp
        if self.bpp == 4:
            w = self.buf[offset + 3]
            if w != 0:
                return w << 16 | w << 8 | w
        return self.buf[offset + 1] << 16 | self.buf[offset] << 8 | self.buf[offset + 2]

    def __len__(self):
        return len(self.buf) // self.bpp

def map_range(x, in_min, in_max, out_min, out_max):
    """
    Maps a number from one range to another.
    Note: This implementation handles values < in_min differently than arduino's map function does.
    :return: Returns value mapped to new range
    :rtype: float
    """
    return max(min((x-in_min) * (out_max - out_min) / (in_max-in_min) + out_min, out_max), out_min)
