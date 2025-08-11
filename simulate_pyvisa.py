import pyvisa

# Simulate HP3458A and HP53131A using PyVISA-sim
rm = pyvisa.ResourceManager('pyvisa_sim.yaml@sim')

# HP3458A (GPIB address 22)
hp3458a = rm.open_resource('GPIB0::23::INSTR', write_termination ='\n', read_termination='\n')
print('HP3458A ID:', hp3458a.query('ID?'))
print('HP3458A Error:', hp3458a.query('ERRSTR?'))
# Simulate a reading
hp3458a.write('TRIG SGL')
print('HP3458A Reading:', hp3458a.query('READ?'))


# HP53131A (GPIB address 13)
hp53131a = rm.open_resource('GPIB0::22::INSTR', write_termination ='\n', read_termination='\n')
print('HP53131A ID:', hp53131a.query('*IDN?'))
print('HP53131A Error:', hp53131a.query(':SYST:ERR?'))
# Simulate frequency measurement
hp53131a.write(':CONF:FREQ DEF,DEF,(@1)')
print('HP53131A Frequency:', hp53131a.query(':FETCH?'))
# Simulate period measurement
hp53131a.write(':CONF:PER DEF,DEF,(@1)')
print('HP53131A Period:', hp53131a.query(':FETCH?'))
