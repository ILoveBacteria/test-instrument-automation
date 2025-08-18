from devices import HP3458A, HP53131A
from adapters import PyVisaAdapter


def create_hp3458():
    # adapter = PyVisaAdapter('GPIB0::2::INSTR', '192.168.1.102:5000@proxy')
    # device = HP3458A(name='hp3458', adapter=adapter)
    device = HP3458A('GPIB0::2::INSTR', visa_library='192.168.1.102:5000@proxy')
    device.adapter.connection.timeout = 15000
    device.setup()
    return device


def create_hp53131():
    # adapter = PyVisaAdapter('GPIB0::23::INSTR', "192.168.1.102:5000@proxy", write_termination ='\n', read_termination='\n')
    # return HP53131A('hp53131', adapter)
    device = HP53131A('GPIB0::3::INSTR', visa_library='192.168.1.102:5000@proxy')
    device.setup()
    device.adapter.connection.timeout = 15000
    return device


