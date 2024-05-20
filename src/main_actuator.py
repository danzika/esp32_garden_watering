from umodbus.serial import ModbusRTU
from machine import Pin, ADC, soft_reset
from sys import stderr
from hcsr04 import HCSR04
import dht
from time import sleep_ms

# modbus config
uart_id = 1
slave_addr = 10
rtu_rxtx_pins = (23, 22)
rtu_ctrl_pin = 21

# periferals config
relay_pins = [18, 19]
proximity_trg_pin = 17
proximity_echo_pin = 16
soil_moisture_pin = 36
dht_pin = 4
mux_en_pin = 5


mux_channels = [ [0,0,0,0], [1,0,0,0], [0,1,0,0], [1,1,0,0], [0,0,1,0], [1,0,1,0], [0,1,1,0], [1,1,1,0], [0,0,0,1], [1,0,0,1], [0,1,0,1], [1,1,0,1], [0,0,1,1], [1,0,1,1], [0,1,1,1], [1,1,1,1] ]
channel_selector_pins = [ 12, 13, 14, 27 ]


# sensors/actuators
relays = list(map(lambda x: Pin(x, Pin.OUT, 1), relay_pins))
proximity_sensor = HCSR04(trigger_pin=proximity_trg_pin, echo_pin=proximity_echo_pin)
soil_sensor = ADC(Pin(soil_moisture_pin))
soil_sensor.atten(ADC.ATTN_11DB)
dht_sensor = dht.DHT22(Pin(dht_pin))

mux_en = Pin(mux_en_pin, Pin.OUT, 0)
mux_channel_selectors = list(map(lambda x: Pin(x, Pin.OUT, 0), channel_selector_pins))


# modbus server
rtu_server = ModbusRTU(
    addr=slave_addr,
    pins=rtu_rxtx_pins,
    ctrl_pin=rtu_ctrl_pin,
    uart_id=uart_id
)

def eprint(message: str):
    print(message, file=stderr)

# modbus callbacks
def set_relay(reg_type, address, val):
    try:
        eprint(f"reg_type={reg_type}, address={address}, value={val[0]}")
        relay = relays[address - 1]
        new_val = 1 if val[0] else 0
        rtu_server.set_coil(address, True if new_val == 1 else False)
        relay.value(new_val)
    except Exception as e:
        eprint(e)

def get_temperature(reg_type, address, val):
    try:
        dht_sensor.measure()
        sleep_ms(100)
        t = int(10*dht_sensor.temperature())
        eprint(f"reg_type={reg_type}, address={address}, value={val}, scaled={t}")
        rtu_server.set_hreg(address, t)
    except Exception as e:
        eprint(e)

def get_humidity(reg_type, address, val):
    try:
        h = int(dht_sensor.humidity())
        eprint(f"reg_type={reg_type}, address={address}, value={val}, measured={h}")
        rtu_server.set_hreg(address, h)
    except Exception as e:
        eprint(e)

def get_proximity(reg_type, address, val):
    try:
        p = int(proximity_sensor.distance_mm())
        eprint(f"reg_type={reg_type}, address={address}, value={val}, measured={p}")
        rtu_server.set_hreg(address, p)
    except Exception as e:
        eprint(e)

def get_moisture(reg_type, address, val):
    try:
        m = soil_sensor.read()
        eprint(f"reg_type={reg_type}, address={address}, value={val}, measured={m}")
        rtu_server.set_hreg(address, m)
    except Exception as e:
        eprint(e)

def set_mux_channel(reg_type, address, val):
    mux_en.value(1)
    idx = val[0]
    for i in range(len(mux_channel_selectors)):
        mux_channel_selectors[i].value(mux_channels[idx][i])
    mux_en.value(0)

register_definitions = {
    "COILS": {
        "RELAY_1": {
            "register": 1,
            "len": 1,
            "val": 0,
            "on_set_cb": set_relay
        },
        "RELAY_2": {
            "register": 2,
            "len": 1,
            "val": 0,
            "on_set_cb": set_relay
        }
    },
    "HREGS": {
        "MOISTURE_CHANNEL": {
            "register": 1,
            "len": 1,
            "val": 0,
            "on_set_cb": set_mux_channel
        },
        "TEMPERATURE": {
            "register": 2,
            "len": 1,
            "val": 50,
            "on_get_cb": get_temperature
        },
        "HUMIDITY": {
            "register": 3,
            "len": 1,
            "val": 500,
            "on_get_cb": get_humidity
        },
        "PROXIMITY": {
            "register": 4,
            "len": 1,
            "val": 5000,
            "on_get_cb": get_proximity
        },
        "MOISTURE": {
            "register": 5,
            "len": 1,
            "val": 50000,
            "on_get_cb": get_moisture
        },
    }
}

# setup registers and start modbus server
rtu_server.setup_registers(registers=register_definitions)

while True:
    try:
        result = rtu_server.process()
    except KeyboardInterrupt:
        print('KeyboardInterrupt, stopping RTU client...')
        break
    except Exception as e:
        print('Exception during execution: {}'.format(e))
