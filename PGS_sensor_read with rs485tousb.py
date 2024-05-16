'''
import serial
import time

# Define serial port settings
port = 'COM10'  # Update this with the correct port name on your system
baudrate = 9600  # Set the baud rate according to your device specifications
timeout = 1

# Create a serial connection
ser = serial.Serial(port, baudrate, timeout=timeout)

try:
    if ser.isOpen():
        print(f"Serial port {port} is open.")

        # Create requests for 10 sensors (adjust as needed)
        sensor_requests = [
            bytes.fromhex('00 00 00 01 01 E4 50'),  # Sensor 0 request
            bytes.fromhex('00 01 00 01 01 E5 AC'),  # Sensor 1 request
            bytes.fromhex('00 02 00 01 01 E5 E8'),  # Sensor 2 request
            bytes.fromhex('00 03 00 01 01 E4 14'),  #Sensor 3 request
            bytes.fromhex('00 04 00 01 01 E5 60'), # Sensor 4 request
            bytes.fromhex('00 05 00 01 01 E4 9C')
        ]

        # Send requests for each sensor
        for index, request in enumerate(sensor_requests, start=1):
            ser.write(request)
            print(f"Sent sensor {index} request:", request)

            # Wait for a response (adjust this based on your device response time)
            time.sleep(0.1)

            # Read response
            response = ser.read_all()
            if response:
                print(f"Received response for sensor {index}:", response.hex())
            else:
                print(f"No response received for sensor {index}.")

    else:
        print(f"Could not open serial port {port}.")

except serial.SerialException as e:
    print("Serial connection error:", e)

finally:
    ser.close()  # Close the serial port when finished

'''
'''
# Example-2 to calculate the available space from the sensor

import serial
import time

# Define serial port settings
port = 'COM10'  # Update this with the correct port name on your system
baudrate = 9600  # Set the baud rate according to your device specifications
timeout = 1

# Define the total number of parking spaces
total_spaces = 5  # Change this value based on the actual number of parking spaces

# Create a serial connection
ser = serial.Serial(port, baudrate, timeout=timeout)

try:
    if ser.isOpen():
        print(f"Serial port {port} is open.")

        # Create requests for 5 sensors (adjust as needed)
        sensor_requests = [
            bytes.fromhex('00 00 00 01 01 E4 50'),  # Sensor 0 request
            bytes.fromhex('00 01 00 01 01 E5 AC'),  # Sensor 1 request
            bytes.fromhex('00 02 00 01 01 E5 E8'),  # Sensor 2 request
            bytes.fromhex('00 03 00 01 01 E4 14'),  # Sensor 3 request
            bytes.fromhex('00 04 00 01 01 E5 60')   # Sensor 4 request
        ]

        # Initialize variables to count available spaces
        available_spaces = total_spaces

        # Send requests for each sensor
        for index, request in enumerate(sensor_requests, start=0):
            ser.write(request)
            print(f"Sent sensor {index} request:", request)

            # Wait for a response (adjust this based on your device response time)
            time.sleep(0.1)

            # Read response
            response = ser.read_all()
            if response:
                # Extract the 6th byte from the response
                sixth_byte = response[5]  # Python uses 0-based indexing

                # Check if the 6th byte is 0x00 (sensor engaged) or not
                sensor_status = "Engaged" if sixth_byte == 0x00 else "Disengaged"

                if sensor_status == "Engaged":
                    available_spaces -= 1  # Decrement available spaces if sensor is engaged

                print(f"Received response for sensor {index}: Sensor is {sensor_status}")
            else:
                print(f"No response received for sensor {index}.")

        print(f"Available parking spaces: {available_spaces}/{total_spaces}")

    else:
        print(f"Could not open serial port {port}.")

except serial.SerialException as e:
    print("Serial connection error:", e)

finally:
    ser.close()  # Close the serial port when finished
'''

from machine import UART
import time

uart = UART(2, baudrate=9600, tx=3, rx=1)
uart1 = UART(1, baudrate=9600, tx=16, rx=17)
uart0 = UART(0, baudrate=9600, tx=25, rx=26)

uart0.init()
sensor_requests = ['FA0101F9', 'FA0201FA', 'FA0301FB']
sensor_status = []
zone_id = '01'  # Convert zone_id to a byte

def calculate_sensor_status(response):
    status_byte = response[2:3]
    if status_byte == b'\x01':
        return 1  # Engaged
    elif status_byte == b'\x02':
        return 2  # Disengaged
    elif status_byte == b'\x03':
        return 3  # Error
    else:
        return -1  # Invalid status

def process_sensor_requests():
    global sensor_status
    sensor_status = []
    for request in sensor_requests:
        if request.startswith('FA'):
            uart.write(bytes.fromhex(request))
            time.sleep(2)
            response = uart.read()
            if response and response[0:1] == b'\xF5':
                sensor_status.append(calculate_sensor_status(response))

    # Construct message
    total_sensors = len(sensor_status)
    total_engaged = sensor_status.count(1)
    total_disengaged = sensor_status.count(2)
    total_errors = sensor_status.count(3)
    total_vacancy = total_disengaged
    message = bytearray([0xAA, int(zone_id), total_sensors] + sensor_status + [total_engaged, total_disengaged, total_vacancy, total_errors, 0x55])
    uart1.write(message)
    uart0.write(message)

# Listen for slave ID from the floor controller
while True:
    process_sensor_requests()

'''
#EXAMPLE-3 this is working zone data. the zone controller will request by sending the protocol and capture the response. after capturing the response it will then extract the status data and send it to the floor controller and the display
#from I2C_LCD import I2cLcd
from machine import UART, Pin
import time

#DEFAULT_I2C_ADDR = 0x27
#i2c_lcd = I2C(scl=Pin(14), sda=Pin(13), freq=400000)
#lcd = I2cLcd(i2c_lcd, DEFAULT_I2C_ADDR, 2, 16)

# Initialize UARTs
#uart2 = UART(2, baudrate=9600, tx=Pin(25), rx=Pin(26))
uart2 = UART(2, baudrate=9600, tx=Pin(33), rx=Pin(32))
uart1 = UART(1, baudrate=9600, tx=Pin(16), rx=Pin(17))
# Disable REPL on UART0
uart = UART(0,9600,tx=Pin(3), rx=Pin(1))
uart.init(9600, bits=8, parity=None, stop=1)

sensor_requests = ['FA0101F9', 'FA0201FA', 'FA0301FB']
zone_id = '01'  # Convert zone_id to a byte

def calculate_sensor_status(response):
    status_byte = response[2:3]
    if status_byte == b'\x01':
        return 1  # Engaged
    elif status_byte == b'\x02':
        return 2  # Disengaged
    elif status_byte == b'\x03':
        return 3  # Error
    else:
        return -1  # Invalid status

def process_sensor_requests():
    sensor_status = []
    
    for request in sensor_requests:
        if request.startswith('FA'):
            uart1.write(bytes.fromhex(request))
            time.sleep(2)
            response = uart1.read()
            if response and response[0:1] == b'\xF5':
                sensor_status.append(calculate_sensor_status(response))

    # Construct message
    total_sensors = len(sensor_status)
    total_engaged = sensor_status.count(1)
    total_disengaged = sensor_status.count(2)
    total_errors = sensor_status.count(3)
    total_vacancy = total_disengaged
    message = bytearray([0xAA, int(zone_id), total_sensors] + sensor_status + [total_engaged, total_disengaged, total_vacancy, total_errors, 0x55])
    
    # Write message to UART2 (pins 3, 1) and UART0 (pins 25, 26)
    uart2.write(message)
    #print(message)
    hex_message = ''.join('{:02x}'.format(byte) for byte in message)
    print(hex_message.upper())



# Main loop
while True:
    process_sensor_requests()
    
    '''
       lcd.clear()
       lcd.move_to(0, 0)
       lcd.putstr("DATA")
       lcd.move_to(0, 1)
       lcd.putstr("RECEIVED!")
    '''


