'''
from machine import UART, Pin
import time

# Initialize UARTs
uart1 = UART(1, baudrate=9600, tx=Pin(16), rx=Pin(17), timeout=2000)
uart2 = UART(2, baudrate=9600, tx=Pin(33), rx=Pin(32), timeout=2000)

# Slave IDs and number of zones
slave_ids = [b'\x01', b'\x02', b'\x03']
num_zones = len(slave_ids)

# Function to clear UART buffer
def clear_uart_buffer(uart):
    while uart.any():
        uart.read(1)

# Function to collect data from a single slave
def collect_data_from_slave(slave_id):
    clear_uart_buffer(uart1)

    response = bytearray()
    start_time = time.time()
    while True:
        if uart1.any() > 0:
            byte = uart1.read(1)
            response.extend(byte)
            # Check for start and end of frame markers
            if response[:1] == b'\xDE' and response[-1:] == b'\xE9':
                break
        if time.time() - start_time > 10:
            print("Timeout waiting for response from Slave", slave_id.hex())
            break

    if response:
        print("Raw response from Slave", slave_id.hex(), ":", response.hex())
        print("Valid response from Slave", slave_id.hex(), ":", response.hex())
        return response  # Return the complete response including end marker
    else:
        print("No response from Slave", slave_id.hex())

    return None

# Function to collect and process data from all slaves
def collect_data_from_slaves():
    all_floor_data = []
    total_engaged = 0
    total_disengaged = 0
    total_vacancy = 0
    total_errors = 0

    for slave_id in slave_ids:
        print("Collecting data from Slave", slave_id.hex())
        response = collect_data_from_slave(slave_id)
        time.sleep(2)
        if response:
            all_floor_data.append(response)
            if len(response) >= 10:
                total_engaged += response[-5]
                total_disengaged += response[-4]
                total_vacancy += response[-3]
                total_errors += response[-2]
        
        clear_uart_buffer(uart1)

    # Build the final message
    message = bytearray([0xF4, 0x01, num_zones])
    for floor_data in all_floor_data:
        message.extend(floor_data)

    total_data = bytearray([total_engaged, total_disengaged, total_vacancy, total_errors, 0xD1])
    message.extend(total_data)

    hex_message_with_spaces = ' '.join('{:02x}'.format(byte) for byte in message)
    print("Final Message with Spaces:", hex_message_with_spaces.upper())

    # Send the final message via uart2
    uart2.write(message)

# Main loop to collect data periodically
while True:
    collect_data_from_slaves()
    time.sleep(10)

'''


from machine import UART, Pin
import time

uart1 = UART(1, baudrate=9600, tx=Pin(16), rx=Pin(17))
uart2 = UART(2, baudrate=9600, tx=Pin(33), rx=Pin(32))

slave_ids = [b'\x01', b'\x02', b'\x03']
num_zones = len(slave_ids)

# Function to clear UART buffer
def clear_uart_buffer(uart):
    while uart.any():
        uart.read(1)

# Function to collect data from a single slave
def collect_data_from_slave():
    response = bytearray()
    start_time = time.time()
    while True:
        if uart1.any() > 0:
            byte = uart1.read(1)
            response.extend(byte)
            # Check for start and end of frame markers
            if response[:1] == b'\xDE' and response[-1:] == b'\xE9':
                break
        if time.time() - start_time > 10:
            break

    if response:
        return response  # Return the complete response including end marker
    return None

# Function to collect and process data from all slaves
def collect_data_from_slaves():
    all_floor_data = []
    total_engaged = 0
    total_disengaged = 0
    total_vacancy = 0
    total_errors = 0

    for _ in slave_ids:
        response = collect_data_from_slave()
        time.sleep(0.1)
        if response:
            all_floor_data.append(response)
            if len(response) >= 12:
                total_engaged += response[-7]
                total_disengaged += response[-6]
                total_vacancy += response[-5]
                total_errors += response[-4]

        clear_uart_buffer(uart1)

    # Build the final message
    message = bytearray([0xF4, 0x01, num_zones])
    for floor_data in all_floor_data:
        message.extend(floor_data)

    total_data = bytearray([total_engaged, total_disengaged, total_vacancy, total_errors, 0xD1])
    message.extend(total_data)

    hex_message_with_spaces = ' '.join('{:02x}'.format(byte) for byte in message)
    # Send the final message via uart2
    uart2.write(message)
    print(message)

# Main loop to collect data periodically
while True:
    collect_data_from_slaves()
    time.sleep(1)
