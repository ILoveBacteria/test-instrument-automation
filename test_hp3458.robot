*** Settings ***
Library    HP3458ALibrary.py

*** Test Cases ***
Test DC Voltage Measurement
    [Documentation]    Example test with HP 3458A
    Open Connection    GPIB0::2::INSTR    visa_library=192.168.1.102:5000@proxy
    Configure DCV
    Get Reading
    Close Connection
