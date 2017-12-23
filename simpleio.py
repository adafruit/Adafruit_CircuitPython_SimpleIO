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
import time
try:
    import audioio
except ImportError:
    pass # not always supported by every board!
import array
import digitalio
import pulseio

def tone(pin, frequency, duration=1):
    """
    Generates a square wave of the specified frequency (50% duty cycle)
    on a pin

    :param ~microcontroller.Pin Pin: Pin on which to output the tone
    :param int frequency: Frequency of tone in Hz
    :param int duration: Duration of tone in seconds (optional)
    """
    try:
        length = 4000 // frequency
        square_wave = array.array("H", [0] * length)
        for i in range(length):
            if i < length / 2:
                square_wave.append(0xFFFF)
            else:
                square_wave.append(0x00)
        with audioio.AudioOut(pin, square_wave) as waveform:
            waveform.play(loop=True)
            time.sleep(duration)
            waveform.stop()
    except (NameError, ValueError):
        with pulseio.PWMOut(pin, frequency=frequency, variable_frequency=False) as pwm:
            pwm.duty_cycle = 0x8000
            time.sleep(duration)

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

class Servo:
    """
    Easy control for hobby (3-wire) servos

    :param ~microcontroller.Pin pin: PWM pin where the servo is located.
    :param int min_pulse: Pulse width (microseconds) corresponding to 0 degrees.
    :param int max_pulse: Pulse width (microseconds) corresponding to 180 degrees.

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
    def __init__(self, pin, min_pulse=0.5, max_pulse=2.5):
        self.pwm = pulseio.PWMOut(pin, frequency=50)
        self.min_pulse = min_pulse
        self.max_pulse = max_pulse
        self._angle = None

    @property
    def angle(self):
        """Get and set the servo angle in degrees"""
        return self._angle

    @angle.setter
    def angle(self, degrees):
        """Writes a value in degrees to the servo"""
        self._angle = max(min(180, degrees), 0)
        pulse_width = 0.5 + (self._angle / 180) * (self.max_pulse - self.min_pulse)
        duty_percent = pulse_width / 20.0
        self.pwm.duty_cycle = int(duty_percent * 65535)

    def microseconds_to_angle(self, us): #pylint: disable-msg=no-self-use, invalid-name
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
        self.iopin = digitalio.DigitalInOut(pin)
        self.iopin.switch_to_output()

    @property
    def value(self):
        """The digital logic level of the output pin."""
        return self.iopin.value

    @value.setter
    def value(self, value):
        self.iopin.value = value

class DigitalIn:
    """
    Simple digital input that is valid until soft reset.
    """
    def __init__(self, pin):
        self.iopin = digitalio.DigitalInOut(pin)
        self.iopin.switch_to_input()

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
    t = (x-in_min) * (out_max - out_min) / (in_max-in_min) + out_min
    if out_min <= out_max:
        return max(min(t, out_max), out_min)
    else:
        return min(max(t, out_max), out_min)

