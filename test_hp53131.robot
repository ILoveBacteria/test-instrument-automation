*** Settings ***
Library    HP53131ALibrary.py    GPIB0::3::INSTR    visa_library=pyvisa_sim.yaml@sim

*** Test Cases ***
Test Frequency Measurement
    [Documentation]    Example test to measure frequency
    ${id}=    Get Id
    Log    Connected to: ${id}
    Reset Device
    Measure Frequency    channel=1
    Initiate Wait And Fetch
    ${freq}=    Initiate Wait And Fetch
    Log    Measured Frequency: ${freq} Hz
