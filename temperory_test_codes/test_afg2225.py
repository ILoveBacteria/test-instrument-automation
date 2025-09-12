import pyvisa

from devices import AFG2225


def visa():
    rm = pyvisa.ResourceManager()
    inst = rm.open_resource("ASRL5::INSTR")
    print(inst.query("*IDN?"))
    inst.write("SOURce1:FREQuency 5000")  # Set frequency for channel 1
    
    
def create_pyvisa_connection():
    device = AFG2225('ASRL5::INSTR')
    device.adapter.connection.timeout = 15000
    device.setup()
    return device
    

def channel1(device):
    print("\n--- Configuring Channel 1 ---")
    device.ch1.shape = 'sine'
    device.ch1.frequency = 10000  # 10 kHz
    device.ch1.amplitude = 2.5    # 2.5 Vpp
    device.ch1.offset = 0.5       # 0.5 V DC offset
    device.ch1.phase = 0          # 0 degrees phase
    device.ch1.output_enabled = True

    print(f"CH1 Shape: {device.ch1.shape}")
    print(f"CH1 Frequency: {device.ch1.frequency / 1000} kHz")
    print(f"CH1 Amplitude: {device.ch1.amplitude} Vpp")
    print(f"CH1 Offset: {device.ch1.offset} V")
    print(f"CH1 Phase: {device.ch1.phase} degrees")
    print(f"CH1 Output Enabled: {device.ch1.output_enabled}")
    
    
def channel2(device):
    print("\n--- Configuring Channel 2 ---")
    device.ch2.shape = 'square'
    device.ch2.frequency = 25000  # 25 kHz
    device.ch2.amplitude = 3.0    # 3.0 Vpp
    device.ch2.offset = 0.0       # 0 V DC offset
    device.ch2.phase = 45         # 45 degrees phase shift relative to CH1
    device.ch2.duty_cycle = 75    # 75% duty cycle
    device.ch2.output_enabled = True

    print(f"CH2 Shape: {device.ch2.shape}")
    print(f"CH2 Frequency: {device.ch2.frequency / 1000} kHz")
    print(f"CH2 Amplitude: {device.ch2.amplitude} Vpp")
    print(f"CH2 Offset: {device.ch2.offset} V")
    print(f"CH2 Phase: {device.ch2.phase} degrees")
    print(f"CH2 Duty Cycle: {device.ch2.duty_cycle}%")
    print(f"CH2 Output Enabled: {device.ch2.output_enabled}")
    

def synchronize_phase_and_shifting(device):
    print("\n--- Demonstrating Other Functions ---")
    # Synchronize the phase of both channels
    print("Synchronizing phase of both channels...")
    device.sync_phase()
    print(f"CH1 Phase after sync: {device.ch1.phase} degrees")
    print(f"CH2 Phase after sync: {device.ch2.phase} degrees")

    # Set phase again
    device.ch2.phase = 90
    print(f"\nSet CH2 phase to {device.ch2.phase} degrees.")
    

def main():
    device = AFG2225("ASRL5::INSTR", timeout=5000)
    device.setup()
    device.ch1.frequency = 3  # 2.5 kHz
    device.ch1.amplitude = 2    # 2.5 Vpp
    # channel1(device)

if __name__ == '__main__':
    main()
