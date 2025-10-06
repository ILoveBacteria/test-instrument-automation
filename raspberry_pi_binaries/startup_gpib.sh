#! /bin/sh

sudo modprobe gpib_bitbang gpio_offset=512
sudo gpib_config
sudo chmod 666 /dev/gpib0
python -m pyvisa_proxy --port 5000