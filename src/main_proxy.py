from umodbus.serial import Serial as ModbusRTUMaster
from umodbus.tcp import ModbusTCP
import network
from sys import stderr
from machine import Pin, soft_reset
from time import sleep

uart_id = 1
rtu_rxtx_pins = (23, 22)
rtu_ctrl_pin = 21

slave_addr = 10

rtu_master = ModbusRTUMaster(
    pins=rtu_rxtx_pins,
    ctrl_pin=rtu_ctrl_pin,
    uart_id=uart_id
)

# coil_status = rtu_master.read_coils(slave_addr=slave_addr, starting_addr=1, coil_qty=1)
# coil_status = rtu_master.write_single_coil(slave_addr=slave_addr, output_address=1, output_value=0)
# coil_status = rtu_master.read_coils(slave_addr=slave_addr, starting_addr=1, coil_qty=1)
# coil_status = rtu_master.write_single_coil(slave_addr=slave_addr, output_address=1, output_value=1)
# coil_status = rtu_master.read_coils(slave_addr=slave_addr, starting_addr=1, coil_qty=1)
# coil_status = rtu_master.write_single_coil(slave_addr=slave_addr, output_address=1, output_value=0)
# coil_status = rtu_master.read_coils(slave_addr=slave_addr, starting_addr=1, coil_qty=1)


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.scan()
wlan.connect('dreamworld22', 'Arturek123738')
sleep(5)
wlan.isconnected()

local_ip = wlan.ifconfig()[0]
tcp_port = 502      # port to listen for requests/providing data

tcp_slave = ModbusTCP()

if not tcp_slave.get_bound_status():
    tcp_slave.bind(local_ip=local_ip, local_port=tcp_port)

def eprint(message: str):
    print(message, file=stderr)

def get_remote_relay(reg_type, address, val):
    try:
        # eprint(f"reg_type={reg_type}, address={address}, value={val[0]}")
        rtu_address = address-100
        res = rtu_master.read_coils(slave_addr=slave_addr, starting_addr=rtu_address, coil_qty=1)
        tcp_slave.set_coil(address, True if res[0] == 1 else False)
    except Exception as e:
        eprint(e)

def set_remote_relay(reg_type, address, val):
    try:
        # eprint(f"reg_type={reg_type}, address={address}, value={val[0]}")
        rtu_address = address-100
        rtu_master.write_single_coil(slave_addr=slave_addr, output_address=rtu_address, output_value=val[0])
    except Exception as e:
        eprint(e)

def get_remote_hreg(reg_type, address, val):
    try:
        # eprint(f"reg_type={reg_type}, address={address}, value={val[0]}")
        rtu_address = address-100
        res = rtu_master.read_holding_registers(slave_addr=slave_addr, starting_addr=rtu_address, register_qty=1)
        tcp_slave.set_hreg(address, res[0])
    except Exception as e:
        eprint(e)

def set_remote_hreg(reg_type, address, val):
    try:
        # eprint(f"reg_type={reg_type}, address={address}, value={val[0]}")
        rtu_address = address-100
        rtu_master.write_single_register(slave_addr=slave_addr, register_address=rtu_address, register_value=val[0])
    except Exception as e:
        eprint(e)

register_definitions = {
    "COILS": {
        "REMOTE_RELAY_1": {
            "register": 101,
            "len": 1,
            "val": 1,
            "on_get_cb": get_remote_relay,
            "on_set_cb": set_remote_relay
        },
        "REMOTE_RELAY_2": {
            "register": 102,
            "len": 1,
            "val": 1,
            "on_get_cb": get_remote_relay,
            "on_set_cb": set_remote_relay
        },
    },
    "HREGS": {
        "MOISTURE_CHANNEL": {
            "register": 101,
            "len": 1,
            "val": 0,
            "on_set_cb": set_remote_hreg,
            "on_get_cb": get_remote_hreg,
        },
        "TEMPERATURE": {
            "register": 102,
            "len": 1,
            "val": 50,
            "on_get_cb": get_remote_hreg
        },
        "HUMIDITY": {
            "register": 103,
            "len": 1,
            "val": 500,
            "on_get_cb": get_remote_hreg
        },
        "PROXIMITY": {
            "register": 104,
            "len": 1,
            "val": 5000,
            "on_get_cb": get_remote_hreg
        },
        "MOISTURE": {
            "register": 105,
            "len": 1,
            "val": 50000,
            "on_get_cb": get_remote_hreg
        }
    }
}

# use the defined values of each register type provided by register_definitions
tcp_slave.setup_registers(registers=register_definitions)

while True:
    try:
        result = tcp_slave.process()
    except KeyboardInterrupt:
        print('KeyboardInterrupt, stopping TCP client...')
        break
    except Exception as e:
        print('Exception during execution: {}'.format(e))
