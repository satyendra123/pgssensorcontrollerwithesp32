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

import machine
import time
from machine import UART, Pin
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd

# Reassign GPIO9 and GPIO10 for UART1
machine.UART(1).init(baudrate=9600, rx=9, tx=10)

# Define RS485 port settings
rs485_port_sensor = UART(1, baudrate=9600)  # UART1 for sensor
rs485_port_output = UART(2, baudrate=9600)  # UART2 for output
rs485_port_vacancy = UART(0, baudrate=9600)  # UART0 for vacancy status

# Define the zone address and total sensors
zone_address = 0x01  # Change this to the actual zone address
total_sensors = 5  # Change this value based on the actual number of sensors in the zone

# I2C LCD settings
i2c = machine.I2C(0, scl=machine.Pin(19), sda=machine.Pin(18), freq=400000)  # Update pins as per your ESP32 board
lcd = I2cLcd(i2c, 0x27, 2, 16)  # I2C address, number of rows, number of columns

try:
    # Initialize variables to count sensor statuses
    total_engaged = 0
    total_disengaged = 0
    total_working_sensors = 0
    total_faulty_sensors = 0

    # Create requests for 5 sensors (adjust as needed)
    sensor_requests = [
        bytes.fromhex('00 00 00 01 01 E4 50'),  # Sensor 0 request
        bytes.fromhex('00 01 00 01 01 E5 AC'),  # Sensor 1 request
        bytes.fromhex('00 02 00 01 01 E5 E8'),  # Sensor 2 request
        bytes.fromhex('00 03 00 01 01 E4 14'),  # Sensor 3 request
        bytes.fromhex('00 04 00 01 01 E5 60')   # Sensor 4 request
    ]

    # Initialize list to store sensor data
    sensor_data = []

    # Send requests for each sensor
    for index, request in enumerate(sensor_requests, start=0):
        rs485_port_sensor.write(request)
        print(f"Sent sensor {index} request:", request)

        # Wait for a response (adjust this based on your device response time)
        time.sleep(0.1)

        # Read response
        response = rs485_port_sensor.read(7)  # Assuming response is 7 bytes long
        if response:
            # Extract the 6th byte from the response
            sixth_byte = response[5]  # MicroPython uses 0-based indexing

            # Check sensor status and update variables
            if sixth_byte == 0x00:  # Engaged
                sensor_data.append(0x01)
                total_engaged += 1
                total_working_sensors += 1
            elif sixth_byte == 0x01:  # Disengaged
                sensor_data.append(0x00)
                total_disengaged += 1
                total_working_sensors += 1
            else:  # Assume faulty or no communication
                sensor_data.append(0x02)  # Assume faulty
                total_faulty_sensors += 1

            print(f"Received response for sensor {index}: Sensor status {sixth_byte}")
        else:
            print(f"No response received for sensor {index}. Assuming sensor is faulty.")
            sensor_data.append(0x02)  # Assume faulty
            total_faulty_sensors += 1

    # Construct the message to send to the floor controller
    message = bytearray([
        0xAA,  # Zone head
        zone_address,  # Zone address
        total_sensors,  # Total sensors
    ])
    message.extend(sensor_data)  # Sensor data for each sensor
    message.extend([
        total_engaged,  # Total engaged sensors
        total_disengaged,  # Total disengaged sensors
        total_working_sensors,  # Total working sensors
        total_faulty_sensors,  # Total faulty sensors
        0x55  # End of communication
    ])

    # Send the message to the floor controller
    rs485_port_output.write(message)

    # Send vacancy status through UART
    vacancy_status = total_sensors - total_engaged - total_disengaged
    rs485_port_vacancy.write(bytes([vacancy_status]))

    # Display data on the LCD
    lcd.putstr("TS: {}\n".format(total_sensors))
    lcd.putstr("TD: {}\n".format(total_working_sensors))
    lcd.putstr("ES: {}\n".format(total_engaged))
    lcd.putstr("VS: {}\n".format(total_disengaged))
    lcd.putstr("N: {}\n".format(total_faulty_sensors))
    lcd.putstr("DS: {}\n".format(total_disengaged))

except Exception as e:
    print("Error:", e)
