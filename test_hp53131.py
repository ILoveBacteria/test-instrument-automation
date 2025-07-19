from devices import HP53131A
from adapters.gpib_adapter import PrologixGPIBEthernet
from adapters.pyvisa_adapter import PyVisaAdapter

import time


def create_prologix_connection():
    adapter = PrologixGPIBEthernet('192.168.1.101', address=3, prologix_read_timeout=0.5, socket_read_timeout=15)
    device = HP53131A(name='HP53131A', adapter=adapter)
    device.setup()
    return device


# Scenario 1: Frequency & Period Measurement
def test_frequency(counter):
    print("Testing Frequency Measurement...")
    freq = counter.measure_frequency(channel=1)
    print(f"Measured Frequency: {freq / 1e6:.6f} MHz")
    
    
def test_period(counter):
    print("\nTesting Period Measurement...")
    period = counter.measure_period(channel=1)
    print(f"Measured Period: {period * 1e6:.6f} µs")


def test_frequency_resolution_control(counter):
    print("\nTesting Resolution Control...")
    # Default resolution
    freq_def = counter.measure_frequency(channel=1, expected_value='1MHz')
    print(f"Default Resolution Freq: {freq_def:.4f} Hz")

    # High resolution (slower measurement)
    freq_high_res = counter.measure_frequency(channel=1, expected_value='1MHz', resolution='0.01Hz')
    print(f"High Resolution Freq:    {freq_high_res:.4f} Hz")


def test_frequency_gated(counter):
    print("\nTesting Gated Frequency Measurement...")
    freq = counter.measure_frequency_gated(gate_time=0.1, channel=1)
    print(f"Low Gate Time Frequency: {freq / 1e6:.6f} MHz")

    # High gate time (longer measurement)
    freq_high_gate = counter.measure_frequency_gated(gate_time=5.0, channel=1)
    print(f"High Gate Time Frequency: {freq_high_gate / 1e6:.6f} MHz")


# Scenario 2: Trigger Level Control
def test_frequency_dc_offset(counter):
    print("\nTesting Trigger Level Control...")
    # First, try to measure with the default auto-trigger (at 50% of p-p, around 0V)
    # This will likely fail or time out because the signal never crosses the default trigger level.
    try:
        print("Attempting measurement with default trigger...")
        freq = counter.measure_frequency(channel=1)
        print(f'  -> Measured frequency with default trigger: {freq / 1e6:.3f} MHz')
    except Exception as e:
        print(f"  -> As expected, measurement failed: {e}")

    # Now, set the trigger level to the signal's DC offset
    print("Setting trigger level to +2.0V and remeasuring...")
    counter.set_trigger_level_volts(channel=1, level=2.0)
    freq = counter.measure_frequency(channel=1)
    print(f"  -> Measured Frequency with correct trigger: {freq / 1e6:.3f} MHz")


# Scenario 3: Time Interval (Edge to Edge)
def test_phase_shift(counter):
    print("\nTesting Time Interval (Phase Shift)...")
    # Measure time from rising edge on Ch1 to rising edge on Ch2
    ti_pos_pos = counter.measure_time_interval(start_edge='POS', stop_edge='POS')
    print(f"Rising-to-Rising (90 deg shift): {ti_pos_pos * 1e9:.1f} ns")
    

def test_rise_to_fall_edge(counter):
    print("\nTesting Time Interval (Pulse Width)...")
    # Measure time from the rising edge (start) to the falling edge (stop) of the same signal
    pulse_width = counter.measure_time_interval(start_edge='POS', stop_edge='NEG')
    print(f"Positive Pulse Width (25% duty): {pulse_width * 1e9:.1f} ns")
    
    
# Scenario 4: Averaging Functions
def test_period_interval_averaging(counter):
    print("\nTesting Averaging Functions...")
    print("--- Single Shot Readings ---")
    for i in range(3):
        p = counter.measure_period(channel=1)
        ti = counter.measure_time_interval()
        print(f"  Run {i+1}: Period={p*1e9:.3f} ns, Time Interval={ti*1e9:.3f} ns")

    print("\n--- Averaged Readings (N=100) ---")
    avg_p = counter.measure_period_average(channel=1, num_averages=100)
    avg_ti = counter.measure_time_interval_average(num_averages=100)
    print(f"  Average Period: {avg_p*1e9:.3f} ns")
    print(f"  Average TI:     {avg_ti*1e9:.3f} ns")
    
    
# Scenario 5: Totalizer (Counter)
def test_totalizer(counter):
    print("\nTesting Totalizer (Counter)...")
    print("Setting FG to 100 kHz.")
    counter.start_totalize()
    print("Counting events for exactly 1.0 second...")
    time.sleep(1.0)
    count = counter.stop_and_fetch_totalize()
    print(f"Total events counted: {count}")
   
    
def test_time_based_totalizer(counter):
    print("\nTesting Time-Based Totalizer...")
    print("Setting FG to 1 kHz.")
    print("Counting events for exactly 1.0 second...")
    count = counter.measure_totalize_timed(gate_time=1.0)
    print(f"Total events counted: {count}")


def main():
    device = create_prologix_connection()
    # test_frequency(device)
    # test_period(device)
    # test_frequency_resolution_control(device)
    # test_frequency_gated(device)
    # test_frequency_dc_offset(device)
    # test_phase_shift(device)
    # test_rise_to_fall_edge(device)
    # test_period_interval_averaging(device)
    # test_totalizer(device)
    # test_time_based_totalizer(device)


if __name__ == "__main__":
    main()