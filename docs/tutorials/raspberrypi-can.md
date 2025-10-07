# Setting Up Raspberry Pi for CAN Protocol Communication

This tutorial will guide you through configuring a Raspberry Pi to act as a CAN (Controller Area Network) protocol interface. By following these steps, you can use your Raspberry Pi to communicate with CAN-enabled devices.

## Step 1: Getting Started with the Raspberry Pi

Follow the initial setup steps as described in the [Raspberry Pi GPIB tutorial](https://github.com/ILoveBacteria/test-instrument-automation/blob/master/docs/tutorials/raspberrypi-gpib.md) to prepare your Raspberry Pi with Raspberry Pi OS Lite and connect via SSH.

## Step 2: Install Required Packages and Enable CAN Hardware

1. **Update System Packages**
   ```bash
   sudo apt update
   sudo apt upgrade
   ```

2. **Edit /boot/config.txt to Enable SPI and CAN Overlays**
   Open the config file:
   ```bash
   sudo nano /boot/firmware/config.txt
   ```

   Add or ensure the following lines are present (adjust oscillator and interrupt as needed for your hardware):

   ```
   dtparam=spi=on
   dtoverlay=mcp2515-can0,oscillator=8000000,interrupt=12
   dtoverlay=spi-bcm2835-overlay
   ```
   
   - `oscillator=8000000` is for an 8MHz crystal.
   - `interrupt=12` means MCP2515 INT is connected to GPIO12 (BCM numbering).

3. **Install CAN Utilities**
   ```bash
   sudo apt install can-utils
   ```

4. **Reboot the Raspberry Pi**
   ```bash
   sudo reboot
   ```

5. **Verify CAN Interface Availability**
   After reboot, check for the CAN interface:
   ```bash
   ls /sys/bus/spi/devices/spi0.0/net
   # Output should include: can0
   ```
   You can also inspect the interface details:
   ```bash
   ls /sys/bus/spi/devices/spi0.0/net/can0/
   ```

6. **Set Up CAN Interface (e.g., 500k baudrate)**
   ```bash
   sudo ip link set can0 up type can bitrate 500000 restart-ms 100
   ```
   Check interface status:
   ```bash
   ifconfig
   # Output should show can0 as UP and RUNNING
   ```

## Step 3: Set Up Python Environment for CAN Communication

1. **Install Python and Create Virtual Environment**
   ```bash
   sudo apt -y install python3-pip
   python -m venv .venv
   source .venv/bin/activate
   pip install "python-can-remote~=0.2"
   ```

## Step 4: Run the CAN Remote Server

Every time you want to run the server, activate the virtual environment and start the CAN remote server:
```bash
source .venv/bin/activate
python -m can_remote --interface=socketcan --channel=can0 --bitrate=500000
```

Your Raspberry Pi is now ready to communicate with CAN devices using the MCP2515 interface and Python tools.