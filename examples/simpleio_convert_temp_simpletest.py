"""
'simpleio_convert_temp_simpletest.py'.

=================================================
Converts a temperature value to Celsius or Fahrenheit
"""
from simpleio import *

while True:
    # Convert from Fahrenheit to Celsius
    sensor_1_f = 212  # sensor temperature in degrees Fahrenheit
    sensor_1_c = convert_temp(f=sensor_1_f)
    print("Sensor: %6.2f Fahrenheit = %6.2f Celsius" % (sensor_1_f, sensor_1_c))

    # Convert from Celsius to Fahrenheit
    sensor_2_c = 100  # sensor temperature in degrees Celsius
    sensor_2_f = convert_temp(c=sensor_2_c)
    print("Sensor: %6.2f Celsius = %6.2f Fahrenheit" % (sensor_2_c, sensor_2_f))
