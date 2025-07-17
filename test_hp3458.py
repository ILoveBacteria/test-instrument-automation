from devices import HP3458A
from adapters.gpib_adapter import PrologixGPIBEthernet
from adapters.pyvisa_adapter import PyVisaAdapter

import time


def create_prologix_connection():
    adapter = PrologixGPIBEthernet('192.168.1.101', address=2, prologix_read_timeout=0.5, socket_read_timeout=15)
    device = HP3458A(name='hp3458', adapter=adapter)
    device.setup()
    return device


def test_beep(device):
    device.beep()


def test_dc_autorange(device):
    print("Testing DCV - Autorange...")
    device.conf_function_DCV(mrange=None) # mrange=None enables autorange
    reading = device.get_reading()
    print(f"Measured Voltage: {reading:.6f} V")
    

def test_dc_manaulrange(device):
    print("\nTesting DCV - Manual Range...")
    # Autorange would pick 100V, but we can force it to the 120V range.
    device.conf_function_DCV(mrange=120)
    reading = device.get_reading()
    print(f"Measured Voltage: {reading:.6f} V")
    

def test_Effect_of_NPLC(device):
    print("\nTesting DCV - NPLC Effect...")
    # Low NPLC = Fast, but more noise
    device.conf_function_DCV(mrange=1, nplc=0.1) 
    print("Readings with NPLC=0.1:")
    for _ in range(5):
        print(f"  {device.get_reading():.7f} V")

    # High NPLC = Slow, but more stable and higher resolution
    device.conf_function_DCV(mrange=1, nplc=100)
    print("\nReadings with NPLC=100:")
    for _ in range(5):
        print(f"  {device.get_reading():.8f} V")
        
        
def test_ac_rms_voltage(device):
    """AC measurement takes more time. 15s timeout"""
    print("\nTesting ACV - Sine Wave...")
    device.conf_function_ACV() 
    reading = device.get_reading()
    print(f"Measured RMS Voltage: {reading:.4f} V")
    
    
def test_2wire_ohms(device):
    print("\nTesting 2-Wire Ohms...")
    device.conf_function_OHM2W(mrange=None) # Use autorange for the pot
    print("Turn the potentiometer shaft. Press Ctrl+C to stop.")
    try:
        while True:
            reading = device.get_reading()
            print(f"Measured Resistance: {reading:.2f} Ohms", end='\r')
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nTest stopped.")
        

def test_frequency_high_resolution(device):
    print("\nTesting Frequency - High Resolution...")
    device.conf_function_FREQ(mrange=1, gate_time=1.0) # 1s gate time for high resolution
    reading = device.get_reading()
    print(f"Measured Frequency: {reading:.3f} Hz")
    
    
def test_frequency_low_resolution(device):
    print("\nTesting Frequency - Low Resolution...")
    device.conf_function_FREQ(mrange=1, gate_time=0.01) # 10ms gate time for lower resolution
    reading = device.get_reading()
    print(f"Measured Frequency: {reading:.3f} Hz")


def main():
    device = create_prologix_connection()
    # print(device.temperature())
    # device = create_pyvisa_connection()
    # test_beep(device)
    # test_dc_autorange(device)
    # test_dc_manaulrange(device)
    # test_Effect_of_NPLC(device)
    # test_ac_rms_voltage(device)
    # test_2wire_ohms(device)
    # test_frequency_high_resolution(device)
    # test_frequency_low_resolution(device)
    # print(device.error())


if __name__ == "__main__":
    main()