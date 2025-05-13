from devices.hp3458a import HP3458A
from adapters.gpib_adapter import PrologixGPIBEthernet
from core.parser import ScenarioParser


def test_instrument():
    adapter = PrologixGPIBEthernet('10.22.68.20', address=2, prologix_read_timeout=0.1, socket_read_timeout=15)
    hp3458a = HP3458A(name='hp3458a', adapter=adapter)
    hp3458a.setup()
    hp3458a.send_command('PRESET NORM')
    hp3458a.measure_voltage()
    response = hp3458a.read_response(1024)
    print(response)
    

def test_parsing():
    parser = ScenarioParser('scenario.yaml', 'core/schema.json')
    read = parser.parse()
    print(read)
 
 
if __name__ == '__main__':
    pass
