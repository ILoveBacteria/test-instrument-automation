import pyvisa


rm = pyvisa.ResourceManager("192.168.1.102:5000@proxy")
# TODO: termination in constructor
inst = rm.open_resource("GPIB0::2::INSTR")
# instr.write('END ON')
# instr.write('TRIG HOLD')
inst.write('END ALWAYS')
print(inst.query('ID?'))