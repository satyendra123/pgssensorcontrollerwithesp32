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

    response = bytearray()
    start_time = time.time()
    while True:
        if uart1.any() > 0:
            byte = uart1.read(1)
            response.extend(byte)
            # Check for end of frame marker
            if response[:1] == b'\xDE' and response[-1:] == b'\xE9':
                break
        if time.time() - start_time > 5:
            print("Timeout waiting for response from Slave", slave_id.hex())
            break

    if response:
        print("Raw response from Slave", slave_id.hex(), ":", response.hex())
        print("Valid response from Slave", slave_id.hex(), ":", response.hex())
        return response[:-2]  # Remove the end of frame marker
    else:
        print("No response from Slave", slave_id.hex())

    return None

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

    message = bytearray([0xF4, 0x01, num_zones])
    for floor_data in all_floor_data:
        message.extend(floor_data)

    total_data = bytearray([total_engaged, total_disengaged, total_vacancy, total_errors, 0xD1])
    message.extend(total_data)
    hex_message_with_spaces = ' '.join('{:02x}'.format(byte) for byte in message)
    print("Final Message with Spaces:", hex_message_with_spaces.upper())
    uart2.write(message)

while True:
    collect_data_from_slaves()
    time.sleep(10)
