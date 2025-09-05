*** Settings ***
Library    HP3458ALibrary.py
Library    HP53131ALibrary.py
Library    AFG2225Library.py
Library    Collections

# Suite Setup    Connect Instruments
# Suite Teardown    Disconnect Instruments

*** Variables ***
${HP3458_ADDR}     GPIB0::2::INSTR
${HP53131_ADDR}    GPIB0::3::INSTR
${AFG2225_ADDR}    ASRL5::INSTR

${TEST_FREQ}       1000
${TEST_AMP}        1.0
${TEST_OFFSET}     0.0

*** Keywords ***
Connect Instruments
    AFG2225Library.Open Connection    ${AFG2225_ADDR}
    HP3458ALibrary.Open Connection    ${HP3458_ADDR}    visa_library=192.168.1.102:5000@proxy
    HP53131ALibrary.Open Connection    ${HP53131_ADDR}    visa_library=192.168.1.102:5000@proxy
    Log    Instruments connected successfully

Disconnect Instruments
    AFG2225Library.Close Connection
    HP3458ALibrary.Close Connection
    HP53131ALibrary.Close Connection
    Log    Instruments disconnected successfully

Configure Function Generator
    [Arguments]    ${freq}    ${amp}    ${offset}
    Set Channel Frequency    1    ${freq}
    Set Channel Amplitude    1    ${amp}
    Set Channel Offset       1    ${offset}
    Set Channel Shape        1    sine
    Enable Channel Output    1
    Log    Configured AFG2225: ${freq} Hz, ${amp} Vpp, ${offset} V offset

*** Test Cases ***
# Measure Voltage With HP3458
#     [Documentation]    Configure AFG2225 to output sine, then measure RMS voltage with HP3458
#     Connect Instruments
#     Configure Function Generator    ${TEST_FREQ}    ${TEST_AMP}    ${TEST_OFFSET}
#     Get Channel Frequency    channel=1
#     Configure Acv
#     ${voltage}=    Get Reading
#     Log    Measured RMS Voltage: ${voltage} V
#     Should Be True    ${voltage} > 0.9 and ${voltage} < 1.1
#     Disconnect Instruments

Measure voltage dc and measure frequency
    Connect Instruments
    Set Channel Frequency    1    100000
    Set Channel Amplitude    1    1
    Set Channel Offset       1    0
    Set Channel Shape        1    sine
    Enable Channel Output    1
    Measure Frequency    channel=1
    Initiate Wait And Fetch
    Configure Dcv
    Get Reading
    Disconnect Instruments

# Measure Frequency With HP53131
#     [Documentation]    Use HP53131 (channel 1) to measure frequency from AFG2225
#     Connect Instruments
#     Configure Function Generator    ${TEST_FREQ}    ${TEST_AMP}    ${TEST_OFFSET}
#     Measure Frequency    channel=1
#     ${freq}=    Initiate Wait And Fetch
#     Log    Measured Frequency: ${freq} Hz
#     Should Be Equal As Numbers    ${freq}    ${TEST_FREQ}    1
#     Disconnect Instruments

# Frequency Sweep Test
#     [Documentation]    Sweep frequency on AFG2225 and validate readings on HP53131
#     FOR    ${f}    IN RANGE    1000    10001    1000
#         Configure Function Generator    ${f}    ${TEST_AMP}    ${TEST_OFFSET}
#         Measure Frequency    channel=1
#         ${measured}=    Initiate Wait And Fetch
#         Log    Expected: ${f} Hz, Measured: ${measured} Hz
#         Should Be Equal As Numbers    ${measured}    ${f}    1
#     END
