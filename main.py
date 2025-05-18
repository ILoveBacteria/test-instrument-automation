from devices.hp3458a import HP3458A
from adapters.gpib_adapter import PrologixGPIBEthernet
from core.parser import ScenarioParser
from core.executor import ScenarioExecutor


def test_instrument():
    hp3458a = create_connection()
    hp3458a.setup()
    hp3458a.send_command('PRESET NORM')
    hp3458a.measure_voltage()
    response = hp3458a.read_response(1024)
    print(response)
    

def create_connection():
    adapter = PrologixGPIBEthernet('10.22.68.20', address=2, prologix_read_timeout=0.1, socket_read_timeout=15)
    hp3458a = HP3458A(name='hp3458a', adapter=adapter)
    return hp3458a


def test_beep():
    hp3458a = create_connection()
    hp3458a.beep()
    

def test_parsing():
    parser = ScenarioParser('scenario.yaml', 'schema/schema.json')
    scenario = parser.parse()
    print(scenario)
    

def test_executing():
    parser = ScenarioParser('scenario.yaml', 'schema/schema.json')
    scenario = parser.parse()
    print(scenario)
    
    adapter = PrologixGPIBEthernet('10.22.68.20', address=scenario.address, prologix_read_timeout=0.5, socket_read_timeout=10)
    hp3458a = HP3458A(name='hp3458a', adapter=adapter)
    hp3458a.setup()
    executor = ScenarioExecutor(scenario, hp3458a)
    executor.execute()
 
 
if __name__ == '__main__':
    test_executing()
