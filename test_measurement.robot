*** Settings ***
Library    HP3458ALibrary.py    AS    Multimeter
Library    HP53131ALibrary.py    AS    Counter
Library    AFG2225Library.py    AS    Function

Suite Setup    Connect Instruments
Suite Teardown    Disconnect Instruments

*** Keywords ***
Configure Function Generator
    [Arguments]    ${freq}    ${amp}
    Set Channel Frequency    1    ${freq}
    Set Channel Amplitude    1    ${amp}
    Set Channel Shape        1    sine
    Enable Channel Output    1
    Log    Configured AFG2225: ${freq} Hz, ${amp} Vpp

Connect Instruments
    Function.Open Connection    address=5
    Multimeter.Open Connection    address=2    visa_library=192.168.1.102:5000@proxy
    Counter.Open Connection    address=3    visa_library=192.168.1.102:5000@proxy

Disconnect Instruments
    Function.Close Connection
    Multimeter.Close Connection
    Counter.Close Connection

*** Test Cases ***
Measure Voltage With Multimeter
    [Documentation]    Configure power meter to output 10 DCV, then measure voltage with HP3458
    Configure Dcv
    ${voltage}=    Get Reading
    Should Be True    ${voltage} > 9.9 and ${voltage} < 10.1

Measure frequency With Counter
    Configure Function Generator    100_000    1.0
    Measure Frequency    channel=1
    ${freq}=    Initiate Wait And Fetch
    Should Be True    ${freq} > 99_990 and ${freq} < 100_010
