# test direct RTU from PC to ESP32
from pymodbus.client import ModbusSerialClient as ModbusClient

client = ModbusClient(method='rtu', port='/dev/tty.usbserial-1460', timeout=1, stopbits = 1, bytesize = 8,  parity='N', baudrate= 9600)
client.connect()


client.write_coil(1,1,10)
client.write_coil(2,1,10)

client.write_coil(1,0,10)
client.write_coil(2,0,10)



client.read_holding_registers(1,1,10).registers[0] # moisture channel
client.read_holding_registers(2,1,10).registers[0] # temp
client.read_holding_registers(3,1,10).registers[0] # humidity
client.read_holding_registers(4,1,10).registers[0] # proximity

client.read_holding_registers(1,1,10).registers[0]

client.write_register(1, 0, 10)
client.read_holding_registers(5,1,10).registers[0]

client.write_register(1, 2, 10)
client.read_holding_registers(5,1,10).registers[0]


# test TCP
from pyModbusTCP.client import ModbusClient
client = ModbusClient(host="192.168.2.96", port=502, unit_id=1)


client.write_single_coil(101,0)
client.write_single_coil(101,1)
client.write_single_coil(102,1)
client.write_single_coil(102,0)
client.write_single_coil(102,1)



client.read_holding_registers(reg_addr=102)
client.read_holding_registers(reg_addr=103)
client.read_holding_registers(reg_addr=104)

client.read_holding_registers(reg_addr=101)
client.read_holding_registers(reg_addr=105)
client.write_single_register(reg_addr=101, reg_value=4)
client.read_holding_registers(reg_addr=105)



#
ampy -d1 --port /dev/tty.SLAB_USBtoUART2 -b 115200

picocom /dev/tty.SLAB_USBtoUART -b 115200
