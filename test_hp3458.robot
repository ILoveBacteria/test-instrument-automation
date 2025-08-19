*** Settings ***
Library    HP3458ALibrary.py

*** Test Cases ***
Test DC Voltage Measurement
    [Documentation]    Example test with HP 3458A
    Open Connection    GPIB0::2::INSTR    visa_library=pyvisa_sim.yaml@sim
    ${id}=    Get Id
    Log    Connected to: ${id}
    Reset Device
    Configure DCV
    ${value}=    Get Reading
    Log    Measured Voltage: ${value} V
    Close Connection
