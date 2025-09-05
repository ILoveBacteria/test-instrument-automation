*** Settings ***
Library    AFG2225Library.py

*** Test Cases ***
Configure Channel 1
    Open Connection    ASRL5::INSTR
    Set Channel Shape    1    sine
    Set Channel Frequency    1    1000
    Set Channel Amplitude    1    2.5
    Enable Channel Output    1
    Close Connection
