from devices.hp3458a import HP3458A
from devices.hp53131a import HP53131A
from devices.base import Instrument
from adapters.gpib_adapter import PrologixGPIBEthernet
from test.parser import ScenarioParser

import time


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

    
def test_counter():
    adapter = PrologixGPIBEthernet('10.22.68.20', address=3, prologix_read_timeout=0.5, socket_read_timeout=5)
    hp53131a = HP53131A('counter', adapter)
    hp53131a.setup()
    hp53131a.measure_frequency()
    res = hp53131a.read_response()
    print(res)
    res = adapter.serial_poll()


def run_fetch(inst, count):
    data = []
    start = time.time()
    for i in range(count):
        result = inst.query('FETC1?')
        # data.append(result)
    end = time.time()
    return (end - start), data


def run_read(inst, count):
    data = []
    start = time.time()
    for i in range(count):
        result = inst.query('READ2?')
        # data.append(result)
    end = time.time()
    return (end - start), data


def run_init_fetch(inst: Instrument, count):
    data = []
    start = time.time()
    for i in range(count):
        inst.send_command('INIT1')
        result = inst.query('FETC2?')
        # data.append(result)
    end = time.time()
    return (end - start), data


def test_power():
    adapter = PrologixGPIBEthernet('192.168.1.101', address=13, prologix_read_timeout=3, socket_read_timeout=10)
    inst = Instrument('power meter', adapter)
    count = 100
    r, data = run_init_fetch(inst, count)
    print(f'total of {count} measurements=', r)
    print(r / count)
    print()
    print('\n'. join(data))
 
 
if __name__ == '__main__':
    test_power()
