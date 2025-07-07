from devices.hp3458a import HP3458A
from devices.hp53131a import HP53131A
from devices.base import Instrument
from adapters.gpib_adapter import PrologixGPIBEthernet
from core.parser import ScenarioParser
from core.executor import ScenarioExecutor

import time


def create_connection():
    adapter = PrologixGPIBEthernet('192.168.1.101', address=2, prologix_read_timeout=0.5, socket_read_timeout=15)
    hp3458a = HP3458A(name='hp3458a', adapter=adapter)
    return hp3458a


def test_beep(hp3458a):
    hp3458a.beep()


def test_dc_autorange(hp3458a):
    print("Testing DCV - Autorange...")
    hp3458a.conf_function_DCV(mrange=None) # mrange=None enables autorange
    reading = hp3458a.get_reading()
    print(f"Measured Voltage: {reading:.6f} V")
    

def test_dc_manaulrange(hp3458a):
    print("\nTesting DCV - Manual Range...")
    # Autorange would pick 100V, but we can force it to the 120V range.
    hp3458a.conf_function_DCV(mrange=120)
    reading = hp3458a.get_reading()
    print(f"Measured Voltage: {reading:.6f} V")
    

def test_Effect_of_NPLC(hp3458a):
    print("\nTesting DCV - NPLC Effect...")
    # Low NPLC = Fast, but more noise
    hp3458a.conf_function_DCV(mrange=1, nplc=0.1) 
    print("Readings with NPLC=0.1:")
    for _ in range(5):
        print(f"  {hp3458a.get_reading():.7f} V")

    # High NPLC = Slow, but more stable and higher resolution
    hp3458a.conf_function_DCV(mrange=1, nplc=100)
    print("\nReadings with NPLC=100:")
    for _ in range(5):
        print(f"  {hp3458a.get_reading():.8f} V")
        
        
def test_ac_rms_voltage(hp3458a):
    """AC measurement takes more time. 15s timeout"""
    print("\nTesting ACV - Sine Wave...")
    hp3458a.conf_function_ACV() 
    reading = hp3458a.get_reading()
    print(f"Measured RMS Voltage: {reading:.4f} V")
    
    
def test_2wire_ohms(hp3458a):
    print("\nTesting 2-Wire Ohms...")
    hp3458a.conf_function_OHM2W(mrange=None) # Use autorange for the pot
    print("Turn the potentiometer shaft. Press Ctrl+C to stop.")
    try:
        while True:
            reading = hp3458a.get_reading()
            print(f"Measured Resistance: {reading:.2f} Ohms", end='\r')
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nTest stopped.")
        

def test_frequency_high_resolution(hp3458a):
    print("\nTesting Frequency - High Resolution...")
    hp3458a.conf_function_FREQ(mrange=1, gate_time=1.0) # 1s gate time for high resolution
    reading = hp3458a.get_reading()
    print(f"Measured Frequency: {reading:.3f} Hz")
    
    
def test_frequency_low_resolution(hp3458a):
    print("\nTesting Frequency - Low Resolution...")
    hp3458a.conf_function_FREQ(mrange=1, gate_time=0.01) # 10ms gate time for lower resolution
    reading = hp3458a.get_reading()
    print(f"Measured Frequency: {reading:.3f} Hz")


def main():
    hp3458a = create_connection()
    test_beep(hp3458a)
    # test_dc_autorange(hp3458a)
    # test_dc_manaulrange(hp3458a)
    # test_Effect_of_NPLC(hp3458a)
    # test_ac_rms_voltage(hp3458a)
    # test_2wire_ohms(hp3458a)
    # test_frequency_high_resolution(hp3458a)
    # test_frequency_low_resolution(hp3458a)
    print(hp3458a.get_error())


if __name__ == "__main__":
    main()