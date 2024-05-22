#with request and response. this is the request send from the master controller [AA 01(slave_id) 80(Mode) A0(CMD) NN] to floor controller and capture the response which is DE to E9 and add the protocol[F4,master_address, total_floor, D1(END Byte)] 
from machine import UART, Pin
import time

uart1 = UART(1, baudrate=9600, tx=Pin(16), rx=Pin(17))
uart2 = UART(2, baudrate=9600, tx=Pin(33), rx=Pin(32))

floor_ids = [0x01, 0x02, 0x03]  # Using integers directly for slave IDs
num_floors = len(floor_ids)

# Function to clear UART buffer
def clear_uart_buffer(uart):
    while uart.any():
        uart.read(1)

# Function to send request byte to floor controller
def send_request_to_slave(floor_id):
    request_byte = bytearray([0xAA, floor_id, 0x80, 0xA0, 0x55])
    uart1.write(request_byte)

# Function to collect data from a single slave
def collect_data_from_slave(floor_id):
    send_request_to_slave(floor_id)
    
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

    for floor_id in floor_ids:
        response = collect_data_from_slave(floor_id)
        time.sleep(0.1)
        if response:
            all_floor_data.append(response)
            if len(response) >= 12:
                total_engaged += response[-5]
                total_disengaged += response[-4]
                total_vacancy += response[-3]
                total_errors += response[-2]

        clear_uart_buffer(uart1)

    # Build the final message
    message = bytearray([0xF4, 0x01, num_floors])
    for floor_data in all_floor_data:
        message.extend(floor_data)

    total_data = bytearray([total_engaged, total_disengaged, total_vacancy, total_errors, 0xD1])
    message.extend(total_data)

    hex_message_with_spaces = ' '.join('{:02x}'.format(byte) for byte in message)
    print(f"Master Data with spaces: {hex_message_with_spaces.upper()}")
    uart2.write(message)

# Main loop to collect data periodically
while True:
    collect_data_from_slaves()
    time.sleep(1)



