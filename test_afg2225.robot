*** Settings ***
Library    AFG2225Library.py    ASRL5::INSTR    visa_library=pyvisa_sim.yaml@sim

*** Test Cases ***
Configure Channel 1
    Set Channel Shape    1    sine
    Set Channel Frequency    1    1000
    Set Channel Amplitude    1    2.5
    Enable Channel Output    1
    ${freq}=    Get Channel Frequency    1
    Log    Channel 1 Frequency: ${freq}
