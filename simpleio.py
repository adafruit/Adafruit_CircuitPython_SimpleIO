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

* Author(s): Scott Shawcroft
"""
import time
import sys
try:
    import audioio
except ImportError:
    pass # not always supported by every board!
import array
import digitalio
import pulseio

def tone(pin, frequency, duration=1, length=100):
    """
    Generates a square wave of the specified frequency on a pin

    :param ~microcontroller.Pin Pin: Pin on which to output the tone
    :param float frequency: Frequency of tone in Hz
    :param int length: Variable size buffer (optional)
    :param int duration: Duration of tone in seconds (optional)
    """
    if length * frequency > 350000:
        length = 350000 // frequency
    try:
        # pin with PWM
        #pylint: disable=no-member
        with pulseio.PWMOut(pin, frequency=int(frequency), variable_frequency=False) as pwm:
            pwm.duty_cycle = 0x8000
            time.sleep(duration)
        #pylint: enable=no-member
    except ValueError:
        # pin without PWM
        sample_length = length
        square_wave = array.array("H", [0] * sample_length)
        for i in range(sample_length / 2):
            square_wave[i] = 0xFFFF
        if sys.implementation.version[0] >= 3:
            square_wave_sample = audioio.RawSample(square_wave)
            square_wave_sample.sample_rate = int(len(square_wave) * frequency)
            with audioio.AudioOut(pin) as dac:
                if not dac.playing:
                    dac.play(square_wave_sample, loop=True)
                    time.sleep(duration)
                dac.stop()
        else:
            sample_tone = audioio.AudioOut(pin, square_wave)
            sample_tone.frequency = int(len(square_wave) * frequency)
            if not sample_tone.playing:
                sample_tone.play(loop=True)
                time.sleep(duration)
            sample_tone.stop()



def bitWrite(x, n, b): #pylint: disable-msg=invalid-name
    """
    Based on the Arduino bitWrite function, changes a specific bit of a value to 0 or 1.
    The return value is the original value with the changed bit.
    This function is written for use with 8-bit shift registers

    :param x: numeric value
    :param n: position to change starting with least-significant (right-most) bit as 0
    :param b: value to write (0 or 1)
    """
    if b == 1:
        x |= 1<<n & 255
    else:
        x &= ~(1 << n) & 255
    return x



def shift_in(data_pin, clock, msb_first=True):
    """
    Shifts in a byte of data one bit at a time. Starts from either the LSB or
    MSB.

    .. warning:: Data and clock are swapped compared to other CircuitPython libraries
      in order to match Arduino.

    :param ~digitalio.DigitalInOut data_pin: pin on which to input each bit
    :param ~digitalio.DigitalInOut clock: toggles to signal data_pin reads
    :param bool msb_first: True when the first bit is most significant
    :return: returns the value read
    :rtype: int
    """

    value = 0
    i = 0

    for i in range(0, 8):
        if msb_first:
            value |= ((data_pin.value) << (7-i))
        else:
            value |= ((data_pin.value) << i)
        # toggle clock True/False
        clock.value = True
        clock.value = False
        i += 1
    return value

def shift_out(data_pin, clock, value, msb_first=True):
    """
    Shifts out a byte of data one bit at a time. Data gets written to a data
    pin. Then, the clock pulses hi then low

    .. warning:: Data and clock are swapped compared to other CircuitPython libraries
      in order to match Arduino.

    :param ~digitalio.DigitalInOut data_pin: value bits get output on this pin
    :param ~digitalio.DigitalInOut clock: toggled once the data pin is set
    :param bool msb_first: True when the first bit is most significant
    :param int value: byte to be shifted

    Example for Metro M0 Express:

    .. code-block:: python

        import digitalio
        import simpleio
        from board import *
        clock = digitalio.DigitalInOut(D12)
        data_pin = digitalio.DigitalInOut(D11)
        latchPin = digitalio.DigitalInOut(D10)
        clock.direction = digitalio.Direction.OUTPUT
        data_pin.direction = digitalio.Direction.OUTPUT
        latchPin.direction = digitalio.Direction.OUTPUT

        while True:
            valueSend = 500
            # shifting out least significant bits
            # must toggle latchPin.value before and after shift_out to push to IC chip
            # this sample code was tested using
            latchPin.value = False
            simpleio.shift_out(data_pin, clock, (valueSend>>8), msb_first = False)
            latchPin.value = True
            time.sleep(1.0)
            latchPin.value = False
            simpleio.shift_out(data_pin, clock, valueSend, msb_first = False)
            latchPin.value = True
            time.sleep(1.0)

            # shifting out most significant bits
            latchPin.value = False
            simpleio.shift_out(data_pin, clock, (valueSend>>8))
            latchPin.value = True
            time.sleep(1.0)
            latchpin.value = False
            simpleio.shift_out(data_pin, clock, valueSend)
            latchpin.value = True
            time.sleep(1.0)
    """
    value = value&0xFF
    for i in range(0, 8):
        if msb_first:
            tmpval = bool(value & (1 << (7-i)))
            data_pin.value = tmpval
        else:
            tmpval = bool((value & (1 << i)))
            data_pin.value = tmpval
        # toggle clock pin True/False
        clock.value = True
        clock.value = False

class DigitalOut:
    """
    Simple digital output that is valid until reload.

      :param pin microcontroller.Pin: output pin
      :param value bool: default value
      :param drive_mode digitalio.DriveMode: drive mode for the output
    """
    def __init__(self, pin, **kwargs):
        self.iopin = digitalio.DigitalInOut(pin)
        self.iopin.switch_to_output(**kwargs)

    @property
    def value(self):
        """The digital logic level of the output pin."""
        return self.iopin.value

    @value.setter
    def value(self, value):
        self.iopin.value = value

class DigitalIn:
    """
    Simple digital input that is valid until reload.

      :param pin microcontroller.Pin: input pin
      :param pull digitalio.Pull: pull configuration for the input
    """
    def __init__(self, pin, **kwargs):
        self.iopin = digitalio.DigitalInOut(pin)
        self.iopin.switch_to_input(**kwargs)

    @property
    def value(self):
        """The digital logic level of the input pin."""
        return self.iopin.value

    @value.setter
    def value(self, value): #pylint: disable-msg=no-self-use, unused-argument
        raise AttributeError("Cannot set the value on a digital input.")

def map_range(x, in_min, in_max, out_min, out_max):
    """
    Maps a number from one range to another.
    Note: This implementation handles values < in_min differently than arduino's map function does.

    :return: Returns value mapped to new range
    :rtype: float
    """
    in_range = in_max - in_min
    in_delta = x - in_min
    if in_range != 0:
        mapped = in_delta / in_range
    elif in_delta != 0:
        mapped = in_delta
    else:
        mapped = .5
    mapped *= out_max - out_min
    mapped += out_min
    if out_min <= out_max:
        return max(min(mapped, out_max), out_min)
    return min(max(mapped, out_max), out_min)
