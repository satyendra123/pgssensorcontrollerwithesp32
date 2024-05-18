'''
from machine import UART, Pin
import time

uart1 = UART(1, baudrate=9600, tx=Pin(16), rx=Pin(17), timeout=2000)
uart2 = UART(2, baudrate=9600, tx=Pin(33), rx=Pin(32), timeout=2000)

slave_ids = [b'\x01', b'\x02', b'\x03']
num_zones = len(slave_ids)

def clear_uart_buffer(uart):
    while uart.any():
        uart.read(1)

def collect_data_from_slave(slave_id):
    clear_uart_buffer(uart1)
    uart1.write(slave_id)
    print("Request sent to Slave", slave_id.hex())
    
    time.sleep(2)
    
    response = bytearray()
    start_time = time.time()
    while True:
        if uart1.any() > 0:
            byte = uart1.read(1)
            response.extend(byte)
            if response[-1:] == b'\x55' and len(response) >= 10:
                break
        if time.time() - start_time > 5:
            print("Timeout waiting for response from Slave", slave_id.hex())
            break

    if response:
        print("Raw response from Slave", slave_id.hex(), ":", response.hex())
        if response[0:1] == b'\xAA' and response[1:2] == slave_id and response[-1:] == b'\x55':
            print("Valid response from Slave", slave_id.hex(), ":", response.hex())
            return response
        else:
            print("Invalid or incomplete response from Slave", slave_id.hex(), ":", response.hex())
    else:
        print("No response from Slave", slave_id.hex())

    return None

def collect_data_from_slaves():
    all_zone_data = []
    total_engaged = 0
    total_disengaged = 0
    total_vacancy = 0
    total_errors = 0

    for slave_id in slave_ids:
        print("Collecting data from Slave", slave_id.hex())
        response = collect_data_from_slave(slave_id)
        time.sleep(2)
        if response:
            all_zone_data.append(response)
            if len(response) >= 10:
                total_engaged += response[-5]
                total_disengaged += response[-4]
                total_vacancy += response[-3]
                total_errors += response[-2]
        
        clear_uart_buffer(uart1)

    message = bytearray([0xDE, 0x01, num_zones])
    for zone_data in all_zone_data:
        message.extend(zone_data)

    total_data = bytearray([total_engaged, total_disengaged, total_vacancy, total_errors, 0xE9])
    message.extend(total_data)
    hex_message_with_spaces = ' '.join('{:02x}'.format(byte) for byte in message)
    print("Final Message with Spaces:", hex_message_with_spaces.upper())
    uart2.write(message)
while True:
    collect_data_from_slaves()
    time.sleep(10)
'''
from machine import UART, Pin
import time

uart1 = UART(1, baudrate=9600, tx=Pin(16), rx=Pin(17), timeout=2000)
uart2 = UART(2, baudrate=9600, tx=Pin(33), rx=Pin(32), timeout=2000)

slave_ids = [b'\x01', b'\x02', b'\x03']
num_zones = len(slave_ids)

def clear_uart_buffer(uart):
    while uart.any():
        uart.read(1)

def collect_data_from_slave(slave_id):
    clear_uart_buffer(uart1)
    uart1.write(slave_id)
    print("Request sent to Slave", slave_id.hex())
    
    time.sleep(2)
    
    response = bytearray()
    start_time = time.time()
    while True:
        if uart1.any() > 0:
            byte = uart1.read(1)
            response.extend(byte)
            if response[-1:] == b'\x55' and len(response) >= 10:
                break
        if time.time() - start_time > 5:
            print("Timeout waiting for response from Slave", slave_id.hex())
            break

    if response:
        print("Raw response from Slave", slave_id.hex(), ":", response.hex())
        if response[0:1] == b'\xAA' and response[1:2] == slave_id and response[-1:] == b'\x55':
            print("Valid response from Slave", slave_id.hex(), ":", response.hex())
            return response
        else:
            print("Invalid or incomplete response from Slave", slave_id.hex(), ":", response.hex())
    else:
        print("No response from Slave", slave_id.hex())

    return None

def collect_data_from_slaves():
    all_zone_data = []
    total_engaged = 0
    total_disengaged = 0
    total_vacancy = 0
    total_errors = 0

    for slave_id in slave_ids:
        print("Collecting data from Slave", slave_id.hex())
        response = collect_data_from_slave(slave_id)
        time.sleep(2)
        if response:
            all_zone_data.append(response)
            if len(response) >= 10:
                total_engaged += response[-5]
                total_disengaged += response[-4]
                total_vacancy += response[-3]
                total_errors += response[-2]
        
        clear_uart_buffer(uart1)

    message = bytearray([0xDE, 0x01, num_zones])
    for zone_data in all_zone_data:
        message.extend(zone_data)

    total_data = bytearray([total_engaged, total_disengaged, total_vacancy, total_errors, 0xE9])
    message.extend(total_data)
    hex_message_with_spaces = ' '.join('{:02x}'.format(byte) for byte in message)
    print("Final Message with Spaces:", hex_message_with_spaces.upper())
    uart2.write(message)
while True:
    collect_data_from_slaves()
    time.sleep(10)

#EXAMPLE-2 with CRC check
from machine import UART, Pin
import time

uart1 = UART(1, baudrate=9600, tx=Pin(16), rx=Pin(17), timeout=2000)
uart2 = UART(2, baudrate=9600, tx=Pin(33), rx=Pin(32), timeout=2000)

slave_ids = [b'\x01', b'\x02', b'\x03']
num_zones = len(slave_ids)

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

def verify_crc(data: bytearray) -> bool:
    if len(data) < 3:
        return False
    received_crc = (data[-3] << 8) | data[-2]
    calculated_crc = crc16(data[:-3])
    return received_crc == calculated_crc

def clear_uart_buffer(uart):
    while uart.any():
        uart.read(1)

def collect_data_from_slave(slave_id):
    clear_uart_buffer(uart1)
    uart1.write(slave_id)
    print("Request sent to Slave", slave_id.hex())
    
    time.sleep(2)
    
    response = bytearray()
    start_time = time.time()
    while True:
        if uart1.any() > 0:
            byte = uart1.read(1)
            response.extend(byte)
            if response[-1:] == b'\x55' and len(response) >= 12:  # Adjust length for CRC
                break
        if time.time() - start_time > 5:
            print("Timeout waiting for response from Slave", slave_id.hex())
            break

    if response:
        print("Raw response from Slave", slave_id.hex(), ":", response.hex())
        if response[0:1] == b'\xAA' and response[1:2] == slave_id and response[-1:] == b'\x55' and verify_crc(response):
            print("Valid response from Slave", slave_id.hex(), ":", response.hex())
            return response
        else:
            print("Invalid or incomplete response from Slave", slave_id.hex(), ":", response.hex())
    else:
        print("No response from Slave", slave_id.hex())

    return None

def collect_data_from_slaves():
    all_zone_data = []
    total_engaged = 0
    total_disengaged = 0
    total_vacancy = 0
    total_errors = 0

    for slave_id in slave_ids:
        print("Collecting data from Slave", slave_id.hex())
        response = collect_data_from_slave(slave_id)
        time.sleep(2)
        if response:
            all_zone_data.append(response)
            if len(response) >= 12:
                total_engaged += response[-5]
                total_disengaged += response[-4]
                total_vacancy += response[-3]
                total_errors += response[-2]
        
        clear_uart_buffer(uart1)

    message = bytearray([0xDE, 0x01, num_zones])
    for zone_data in all_zone_data:
        message.extend(zone_data)

    total_data = bytearray([total_engaged, total_disengaged, total_vacancy, total_errors, 0xE9])
    message.extend(total_data)
    hex_message_with_spaces = ' '.join('{:02x}'.format(byte) for byte in message)
    print("Final Message with Spaces:", hex_message_with_spaces.upper())
    uart2.write(message)

while True:
    collect_data_from_slaves()
    time.sleep(10)
