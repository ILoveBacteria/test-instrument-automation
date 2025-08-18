*** Settings ***
Library    HP3458ALibrary.py    GPIB0::2::INSTR    visa_library=pyvisa_sim.yaml@sim

*** Test Cases ***
Test DC Voltage Measurement
    [Documentation]    Example test with HP 3458A
    ${id}=    Get Id
    Log    Connected to: ${id}
    Reset Device
    Configure DCV
    ${value}=    Get Reading
    Log    Measured Voltage: ${value} V
