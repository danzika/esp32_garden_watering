# esp32_garden_watering
Smart garden watering based on ESP32 and MicroPython

The project is developed and tested ONLY using ESP32 (no suffixes). It is possible that it may work just fine
on other platforms, however, this is not tested in my upstream.

The goal of this project tries to provide an ESP32-based microcontroller to read sensor and switch individual valves
in watering system.
Currently the control communication relies on RS485/Modbus-RTU, because of my environment. However, there is no reason
why this communication couldn't be exchanged for Modbus-TCP. It might be implemented later

My setup uses:
- ESP32 board flashed with Micropython-1.22.0
- opto-isolated relay board (for valve switching)
- HC-SR04 ultrasound proximity sensor (water tank level)
- RS485/MAX board for Modbus/RTU communication
- 3.3V/5V level converter
- 16 channel multiplexer (for reading soil moisture sensors)
- DHT21 air temp/humidity sensor

# SW tools
- micropython and esptool: https://micropython.org/download/ESP32_GENERIC/
- ampy: https://pypi.org/project/adafruit-ampy/
- picocom (or alternative) for interactive work with the board
- ESP32 driver for your platform: https://randomnerdtutorials.com/install-esp32-esp8266-usb-drivers-cp210x-mac-os/

# Important
Doc is still catching up my table prototype so it may easily be inaccurate and/or omit some parts.
All the work is still a prototype WIP.