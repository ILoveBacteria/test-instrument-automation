*** Settings ***
Library    HP53131ALibrary.py

*** Test Cases ***
Test Frequency Measurement
    [Documentation]    Example test to measure frequency
    Open Connection    GPIB0::3::INSTR    visa_library=192.168.1.102:5000@proxy
    Measure Frequency    channel=1
    Initiate Wait And Fetch
    Close Connection
