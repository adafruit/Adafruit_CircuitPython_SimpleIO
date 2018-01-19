"""
'map_range_demo.py'.

=================================================
maps a number from one range to another
"""
import time
import simpleio

while True:
    SENSOR_VALUE = 150

    # Map the sensor's range from 0<=SENSOR_VALUE<=255 to 0<=SENSOR_VALUE<=1023
    print('original sensor value: ', SENSOR_VALUE)
    MAPPED_VALUE = simpleio.map_range(SENSOR_VALUE, 0, 255, 0, 1023)
    print('mapped sensor value: ', MAPPED_VALUE)
    time.sleep(2)

    # Map the new sensor value back to the old range
    SENSOR_VALUE = simpleio.map_range(MAPPED_VALUE, 0, 1023, 0, 255)
    print('original value returned: ', SENSOR_VALUE)
    time.sleep(2)
