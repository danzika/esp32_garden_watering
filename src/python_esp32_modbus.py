# micropython - esp32
# picocom /dev/tty.SLAB_USBtoUART -b 115200

from umodbus.serial import ModbusRTU
from machine import Pin, soft_reset
import dht
from sys import stderr
from math import round

def eprint(message: str):
    print(message, file=stderr)

rtu_pins = (23, 22)
uart_id = 1
slave_addr = 10
dht_sensor = dht.DHT22(Pin(5))

client = ModbusRTU(
    addr=slave_addr,
    pins=rtu_pins,
    ctrl_pin=21,
    uart_id=uart_id
)

relay_pins = [Pin(18, Pin.OUT, 1), Pin(19, Pin.OUT, 1)]

def set_relay_pin(reg_type, address, val):
    try:
        eprint(f"reg_type={reg_type}, address={address}, value={val}")
        relay_id = address - 100
        relay = relay_pins[relay_id]
        relay.value(1 if val[0] else 0)
    except Exception as e:
        eprint(e)

def get_temperature(reg_type, address, val):
    try:
        dht_sensor.measure()
        t = dht_sensor.temperature()
        t_scaled = int(t*10)
        eprint(f"reg_type={reg_type}, address={address}, value={val}, measured={t}, scaled={t_scaled}")
        client.set_hreg(address, t_scaled)
        return t
    except Exception as e:
        eprint(e)

def get_humidity(reg_type, address, val):
    try:
        dht_sensor.measure()
        t = dht_sensor.humidity()
        eprint(f"reg_type={reg_type}, address={address}, value={val}, measured={t}")
        val[0] = t
    except Exception as e:
        eprint(e)


register_definitions = {
    "COILS": {
        "RELAY_1": {
            "register": 100,
            "len": 1,
            "val": 0,
            "on_set_cb": set_relay_pin
        },
        "RELAY_2": {
            "register": 101,
            "len": 1,
            "val": 0,
            "on_set_cb": set_relay_pin
        }
    },
    "HREGS": {
        "TEMPERATURE": {
            "register": 1,
            "len": 1,
            "val": 50,
            "on_get_cb": get_temperature
        },
        "HUMIDITY": {
            "register": 2,
            "len": 1,
            "val": 100,

        }
    },
    "ISTS": {
        "EXAMPLE_ISTS": {
            "register": 67,
            "len": 1,
            "val": 0
        }
    },
    "IREGS": {
        "EXAMPLE_IREG": {
            "register": 10,
            "len": 1,
            "val": 60001
        }
    }
}

client.setup_registers(registers=register_definitions)

while True:
    try:
        result = client.process()
    except KeyboardInterrupt:
        print('KeyboardInterrupt, stopping RTU client...')
        break
    except Exception as e:
        print('Exception during execution: {}'.format(e))


# read from ultra-sonic proximity sensor
from hcsr04 import HCSR04
sensor = HCSR04(trigger_pin=22, echo_pin=23, echo_timeout_us=30000)
sensor.distance_cm()

# read from soil mositure sensor
from machine import Pin, ADC
soil_moisture = ADC(Pin(13))
soil_moisture.atten(ADC.ATTN_11DB)
soil_moisture.read()





# PC python console
from pymodbus.client import ModbusSerialClient as ModbusClient

client = ModbusClient(method='rtu', port='/dev/tty.usbserial-1420', timeout=1, stopbits = 1, bytesize = 8,  parity='N', baudrate= 9600)
client.connect()

client.read_holding_registers(93,1,10).registers[0]
