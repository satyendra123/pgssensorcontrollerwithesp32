#EXAMPLE-1 now i want that if i send the request from the floor controller to the zone controller then only it sends me the response
from machine import UART, Pin
import time

# Initialize UARTs
uart2 = UART(2, baudrate=9600, tx=Pin(33), rx=Pin(32))
uart1 = UART(1, baudrate=9600, tx=Pin(16), rx=Pin(17))
# Disable REPL on UART0
uart = UART(0, 9600, tx=Pin(3), rx=Pin(1))
uart.init(9600, bits=8, parity=None, stop=1)

sensor_requests = ['FA0101F9', 'FA0201FA', 'FA0301FB']
sensor_status = []
zone_id = b'\x02'  # Convert zone_id to a byte

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
            uart1.write(bytes.fromhex(request))
            time.sleep(2)  # Adjust the sleep time as needed for your hardware
            response = uart1.read()
            if response and response[0:1] == b'\xF5':
                sensor_status.append(calculate_sensor_status(response))
    
    # Construct message
    total_sensors = len(sensor_status)
    total_engaged = sensor_status.count(1)
    total_disengaged = sensor_status.count(2)
    total_errors = sensor_status.count(3)
    total_vacancy = total_disengaged
    message = bytearray([0xAA, int.from_bytes(zone_id, "little"), total_sensors] + sensor_status + [total_engaged, total_disengaged, total_vacancy, total_errors, 0x55])
    uart2.write(message)
    display = bytearray([0xDD, int.from_bytes(zone_id, "little"), total_vacancy, 0xFF])
    hex_display = ''.join('{:02x}'.format(byte) for byte in display)
    print(hex_display.upper())

# Listen for slave ID from the floor controller
while True:
    if uart2.any():
        received_data = uart2.read()
        if received_data:
            slave_id = received_data[0:1]  # Read the first byte as slave ID
            if slave_id == zone_id:
                process_sensor_requests()
    time.sleep(0.1)  # Small delay to prevent high CPU usage

'''
#EXAMPLE-2
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
    display = bytearray([0xDD, int.from_bytes(zone_id, "little"), total_vacancy, 0xFF])
    hex_display = ''.join('{:02x}'.format(byte) for byte in display)
    print(hex_display.upper())

# Main loop
while True:
    process_sensor_requests()
'''
#EXAMPLE-3 zone controller2 with CRC check
'''
from machine import UART, Pin
import time

# Initialize UARTs
uart2 = UART(2, baudrate=9600, tx=Pin(33), rx=Pin(32))
uart1 = UART(1, baudrate=9600, tx=Pin(16), rx=Pin(17))
# Disable REPL on UART0
uart = UART(0, 9600, tx=Pin(3), rx=Pin(1))
uart.init(9600, bits=8, parity=None, stop=1)

sensor_requests = ['FA0101F9', 'FA0201FA','FA0301FB']
zone_id = b'\x02'  # Change this for each zone controller (e.g., b'\x02' for zone 2)

def crc16(data: bytearray) -> int:
    crc = 0x0000
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if (crc & 0x8000) != 0:
                crc = (crc << 1) ^ 0x1021
            else:
                crc = crc << 1
        crc &= 0xFFFF  # Ensure CRC remains 16-bit
    return crc

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
            time.sleep(0.1)
            response = uart1.read()
            if response and response[0:1] == b'\xF5':
                sensor_status.append(calculate_sensor_status(response))
            else:
                sensor_status.append(0)
    # Construct message
    total_sensors = len(sensor_requests)
    total_engaged = sensor_status.count(1)
    total_disengaged = sensor_status.count(2)
    total_errors = sensor_status.count(3)
    total_vacancy = total_disengaged
    message = bytearray([0xAA, int.from_bytes(zone_id, "little"), total_sensors] + sensor_status + [total_engaged, total_disengaged, total_vacancy, total_errors])
    
    # Calculate CRC-16
    crc = crc16(message)
    message.append(crc >> 8)  # Append high byte of CRC
    message.append(crc & 0xFF)  # Append low byte of CRC
    message.append(0x55)
    uart2.write(message)
    
    # Display part (uncomment if needed)
    display = bytearray([0xDD, int.from_bytes(zone_id, "little"), total_vacancy, 0xFF])
    hex_display = ''.join('{:02x}'.format(byte) for byte in display)
    print(hex_display.upper())

# Listen for commands from the floor controller
while True:
    if uart2.any():
        received_data = uart2.read()
        if received_data:
            # Check if the received data matches the expected format
            if len(received_data) == 5 and received_data[0:1] == b'\xAA' and received_data[4:5] == b'\x55':
                command_zone_id = received_data[1:2]
                if command_zone_id == zone_id:
                    process_sensor_requests()
    time.sleep(1)

'''
#EXAMPLE-4 this is my final zone2 controller code. in this code i am sending the different protocol because i am integrating this with nand sir p10 display. and this is working fine

from machine import UART, Pin
import time

# Initialize UARTs
uart2 = UART(2, baudrate=9600, tx=Pin(33), rx=Pin(32))
uart1 = UART(1, baudrate=9600, tx=Pin(16), rx=Pin(17))
# Disable REPL on UART0
uart = UART(0, 9600, tx=Pin(3), rx=Pin(1))
uart.init(9600, bits=8, parity=None, stop=1)

sensor_requests = ['FA0101F9', 'FA0201FA', 'FA0301FB']
zone_id = b'\x02'  # Change this for each zone controller (e.g., b'\x02' for zone 2)

def crc16(data: bytearray) -> int:
    crc = 0x0000
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if (crc & 0x8000) != 0:
                crc = (crc << 1) ^ 0x1021
            else:
                crc = crc << 1
        crc &= 0xFFFF  # Ensure CRC remains 16-bit
    return crc

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
            time.sleep(0.1)
            response = uart1.read()
            if response and response[0:1] == b'\xF5':
                sensor_status.append(calculate_sensor_status(response))
            else:
                sensor_status.append(0)
    # Construct message
    total_sensors = len(sensor_requests)
    total_engaged = sensor_status.count(1)
    total_disengaged = sensor_status.count(2)
    total_errors = sensor_status.count(3)
    total_vacancy = total_disengaged
    message = bytearray([0xAA, int.from_bytes(zone_id, "little"), total_sensors] + sensor_status + [total_engaged, total_disengaged, total_vacancy, total_errors])
    
    # Calculate CRC-16
    crc = crc16(message)
    message.append(crc >> 8)  # Append high byte of CRC
    message.append(crc & 0xFF)  # Append low byte of CRC
    message.append(0x55)
    uart2.write(message)
    
    # Display part
    slots_str = f'{total_vacancy:02d}'
    display_message = f'|C|1|4|1|28-0-#u{slots_str}|'
    print(display_message)

# Listen for commands from the floor controller
while True:
    if uart2.any():
        received_data = uart2.read()
        if received_data:
            # Check if the received data matches the expected format
            if len(received_data) == 5 and received_data[0:1] == b'\xAA' and received_data[4:5] == b'\x55':
                command_zone_id = received_data[1:2]
                if command_zone_id == zone_id:
                    process_sensor_requests()
    time.sleep(1)



