*** Settings ***
Library    HP3458ALibrary.py    GPIB0::2::INSTR    visa_library=pyvisa_sim.yaml@sim

*** Test Cases ***
Measure DC Voltage
    [Documentation]    Setup HP3458A and measure DC voltage
    Setup Device
    Configure DCV    mrange=None
    ${reading}=    Get Reading
    Log    The measured value is ${reading}
    # [Teardown]    Reset Device
