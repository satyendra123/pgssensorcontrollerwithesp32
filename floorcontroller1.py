#floor controller
from machine import UART, Pin
import time

# Initialize UARTs
uart2 = UART(2, baudrate=9600, tx=Pin(33), rx=Pin(32))
uart1 = UART(1, baudrate=9600, tx=Pin(16), rx=Pin(17))
uart0 = UART(0, 9600, tx=Pin(1), rx=Pin(3))

# Slave IDs
slave_ids = [b'\x01', b'\x02', b'\x03']
num_zones = len(slave_ids)

def collect_data_from_slaves():
    all_zone_data = []
    total_engaged = 0
    total_disengaged = 0
    total_vacancy = 0
    total_errors = 0
    
    for slave_id in slave_ids:
        uart2.write(slave_id)
        time.sleep(0.5)
        response = uart2.read()  
        if response and response[0:1] == b'\xAA' and response[-1:] == b'\x55' and response[1:2] == slave_id:
            print("Received data from Slave:", slave_id.hex())
            all_zone_data.append(response[2:-5])
            total_engaged += response[-5]
            total_disengaged += response[-4]
            total_vacancy += response[-3]
            total_errors += response[-2]
    
    message = bytearray([0xDE, 0x01, num_zones])
    for zone_data in all_zone_data:
        message.extend(zone_data)

    message.extend([total_engaged, total_disengaged, total_vacancy, total_errors, 0xE9])
    
    uart1.write(message)
    hex_message = ''.join('{:02x}'.format(byte) for byte in message)
    print("Final Message:", hex_message.upper())

while True:
    collect_data_from_slaves()
    time.sleep(10)

