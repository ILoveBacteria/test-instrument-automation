from devices.hp3458a import HP3458A
from adapters.gpib_adapter import PrologixGPIBEthernet


def main():
    adapter = PrologixGPIBEthernet('10.22.68.20', address=2, prologix_read_timeout=2, socket_read_timeout=5)
    hp3458a = HP3458A(name='hp3458a', adapter=adapter)
    hp3458a.setup()
    # hp3458a.measure_voltage()
    # hp3458a.write('RESET')
    # hp3458a.write('TBUFF ON')
    # hp3458a.measure_voltage_interval(interval=100, count=10)
    # hp3458a.beep()
    # hp3458a.wait_for_data()
    hp3458a.temperature()
    # hp3458a.reading_counts()
    # hp3458a.error()
    response = hp3458a.read_response()
    print(response)
    
    
if __name__ == '__main__':
    main()
    