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

The `simpleio` module contains classes to provide simple access to IO.
"""

import digitalio
import pulseio
import math
import time

def shift_in(dataPin, clock, msb_first=True):
    """
    Shifts in a byte of data one bit at a time. Starts from either the LSB or
    MSB.

    .. warning:: Data and clock are swapped compared to other CircuitPython libraries
      in order to match Arduino.

    :param ~digitalio.DigitalInOut dataPin: pin on which to input each bit
    :param ~digitalio.DigitalInOut clock: toggles to signal dataPin reads
    :param bool msb_first: True when the first bit is most significant
    :return: returns the value read
    :rtype: int
    """

    value = 0
    i = 0

    for i in range(0, 8):
        clock.value = True
        if msb_first:
            value |= ((dataPin.value) << (7-i))
        else:
            value |= ((dataPin.value) << i)
        clock.value = False
        i+=1
    return value

def shift_out(dataPin, clock, value, msb_first=True):
    """
    Shifts out a byte of data one bit at a time. Data gets written to a data
    pin. Then, the clock pulses hi then low

    .. warning:: Data and clock are swapped compared to other CircuitPython libraries
      in order to match Arduino.

    :param ~digitalio.DigitalInOut dataPin: value bits get output on this pin
    :param ~digitalio.DigitalInOut clock: toggled once the data pin is set
    :param bool msb_first: True when the first bit is most significant
    :param int value: byte to be shifted

    Example for Metro M0 Express:

    .. code-block:: python

        import digitalio
        import simpleio
        from board import *
        clock = digitalio.DigitalInOut(D12)
        dataPin = digitalio.DigitalInOut(D11)
        clock.direction = digitalio.Direction.OUTPUT
        dataPin.direction = digitalio.Direction.OUTPUT

        while True:
            valueSend = 500
            # shifting out least significant bits
            simpleio.shift_out(dataPin, clock, (valueSend>>8), msb_first = False)
            simpleio.shift_out(dataPin, clock, valueSend, msb_first = False)
            # shifting out most significant bits
            simpleio.shift_out(dataPin, clock, (valueSend>>8))
            simpleio.shift_out(dataPin, clock, valueSend)
    """
    value = value&0xFF
    for i in range(0, 8):
        if msb_first:
            tmpval = bool(value & (1 << (7-i)))
            dataPin.value = tmpval
        else:
            tmpval = bool((value & (1 << i)))
            dataPin.value = tmpval

class Servo:
    """
    Easy control for hobby (3-wire) servos

    :param ~microcontroller.Pin pin: PWM pin where the servo is located.
    :param int min_pulse: Minimum amount of microseconds allowed. Varies depending on type of servo.
    :param int max_pulse: Maximum amount of microseconds allowed. Varies depending on type of servo.

    Example for Metro M0 Express:

    .. code-block:: python

        import simpleio
        import time
        from board import *

        pwm = simpleio.Servo(D9)

        while True:
            pwm.angle = 0
            print("Angle: ", pwm.angle)
            time.sleep(2)
            pwm.angle = pwm.microseconds_to_angle(2500)
            print("Angle: ", pwm.angle)
            time.sleep(2)
    """
    def __init__(self, pin, min_pulse = 0.5, max_pulse = 2.5):
        self.pwm = pulseio.PWMOut(pin, frequency = 50)
        self.min_pulse = min_pulse
        self.max_pulse = max_pulse
        self._angle = 90
        self._microseconds = 0

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, degrees):
        """Writes a value in degrees to the servo"""
        self._angle = max(min(180, degrees), 0)
        pulseWidth = 0.5 + (self._angle / 180) * (self.max_pulse - self.min_pulse)
        dutyPercent = pulseWidth / 20.0
        self.pwm.duty_cycle = int(dutyPercent * 65535)

    def microseconds_to_angle(self, us):
        """Converts microseconds to a degree value"""
        return map_range(us, 500, 2500, 0, 180)

    def deinit(self):
        """Detaches servo object from pin, frees pin"""
        self.pwm.deinit()

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

def map_range(x, in_min, in_max, out_min, out_max):
    """
    Maps a number from one range to another.
    Note: This implementation handles values < in_min differently than arduino's map function does.

    :return: Returns value mapped to new range
    :rtype: float
    """
    return max(min((x-in_min) * (out_max - out_min) / (in_max-in_min) + out_min, out_max), out_min)
