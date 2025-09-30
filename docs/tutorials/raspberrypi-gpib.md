# Setting Up Raspberry Pi as a GPIB Protocol Converter

This tutorial will guide you through the process of configuring a Raspberry Pi to act as a GPIB (General Purpose Interface Bus) protocol converter. By following these steps, you can use your Raspberry Pi to interface with test and measurement instruments that communicate over the GPIB protocol. This setup is ideal for creating a low-cost, flexible solution for automating laboratory instruments.

## Step 1: Getting Started with the Raspberry Pi

### Hardware Requirements
- **Raspberry Pi 3 Model B+** (or newer)
- **MicroSD Card**: At least 16 GB is recommended
- **Power Supply**: Compatible with your Raspberry Pi model
- **Ethernet Cable or Wi-Fi**: For network connectivity

### Download Raspberry Pi OS
1. Visit the official Raspberry Pi website to download the operating system: [Raspberry Pi OS Downloads](https://www.raspberrypi.com/software/operating-systems/).
2. Download **Raspberry Pi OS Lite (32-bit)**, version **6.12** (Bookworm), released on **13 May 2025**. The file size is approximately **493 MB**.

### Optional: Verify the Integrity of the Download
To ensure the downloaded file is not corrupted, you can verify its integrity using the following Python script:

```python
import hashlib

with open('path/to/2025-05-13-raspios-bookworm-armhf-lite.img.xz', 'rb') as file:
    data = file.read().strip()
hash_object = hashlib.sha256()
hash_object.update(data)
digest = hash_object.hexdigest()
print("SHA-256 Digest:", digest)
```
Replace `'path/to/2025-05-13-raspios-bookworm-armhf-lite.img.xz'` with the actual path to the downloaded file. Compare the output with the checksum provided on the Raspberry Pi website.

### Flash Raspberry Pi OS to the SD Card

1. **Install Raspberry Pi Imager**:
   Download and install the Raspberry Pi Imager app from the official website: [Raspberry Pi Imager](https://www.raspberrypi.com/software/).

2. **Open the Imager App**:
   Launch the Raspberry Pi Imager on your computer.

3. **Select Your Device Model**:
   Choose your Raspberry Pi model (e.g., Raspberry Pi 3 Model B+).

4. **Choose Operating System**:
   Scroll down and select **"Use custom"**. Then, browse and select the downloaded OS file (`.img.xz`).

5. **Select Storage**:
   Choose your SD card from the list of available storage devices.

6. **Configure OS Settings (Optional)**:
   - If prompted for custom OS settings, click **"Edit settings"**.
   - You can set a custom username and password.
   - If you do not set a username and password, the default credentials will be used.
   - Save your settings and confirm.

7. **Write the OS to the SD Card**:
   Click **"Next"** and then **"Yes"** to start writing the OS to the SD card.
   Wait for the process to complete before removing the SD card from your computer.

### Boot and Connect to Your Raspberry Pi

1. **Insert the SD Card**:
   Place the prepared SD card into your Raspberry Pi.

2. **Power On**:
   Connect the power supply to your Raspberry Pi and turn it on.

3. **Connect to Router**:
   - If you are using Ethernet, connect the Raspberry Pi to your router using an Ethernet cable.

4. **Find the IP Address**:
   - Check your router's dashboard or connected devices list to find the IP address assigned to your Raspberry Pi.

5. **SSH into the Raspberry Pi**:
   - Open a terminal on your computer.
   - Connect via SSH using the default username (`pi`) and the IP address you found:
     ```bash
     ssh pi@192.168.1.175
     ```
   - Replace `192.168.1.175` with the actual IP address of your device.

You should now have remote access to your Raspberry Pi and be ready for further setup steps.