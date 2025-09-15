# What is this?

During **Research and Development** of a Test Instrument Automation Framework, I wrote some temporary test codes to try out various functionalities and features. These codes are not part of the main framework but were created to experiment with different ideas and implementations. They may include scripts, snippets, or small programs that helped me understand how certain components work or how to integrate them into the larger framework. These temporary test codes are essential for the development process as they allow me to validate concepts before incorporating them into the main project.

## Files in this Directory

- `scenario.yaml`: At the beginning of the project, my first idea to implement a test scenario parser was to use YAML files. However, I decided to use *Robot Framework* test cases as the test scenario files. This file is no longer used in the project.
- `scenario_builder.py`: A Streamlit-based tool for dynamically generating user interfaces to configure instrument functions and parameters.
- `simulate_pyvisa.py`: Simulates the behavior of HP3458A and HP53131A instruments using PyVISA-sim for testing without physical hardware.
- `test.py`: Demonstrates the setup and communication with the HP3458A instrument using a Prologix GPIB-Ethernet adapter.
- `test_afg2225.py`: Contains test cases for the AFG2225 function generator, including PyVISA-based communication setup.
- `test_hp3458.py`: Tests the HP3458A multimeter using both Prologix and PyVISA connections.
- `test_hp53131.py`: Tests the HP53131A frequency counter using Prologix and PyVISA connections.
- `test_low_level.py`: A low-level GPIB communication example using the `Gpib` library.
- `test_openhtf.py`: Placeholder for OpenHTF-based test scenarios.
- `test_pyvisa_proxy.py`: Placeholder for testing PyVISA proxy setups.
- `test_redis_publisher.py`: Mock for Redis-based message publishing tests.
- `test_srq.py`: Placeholder for testing Service Request (SRQ) handling.