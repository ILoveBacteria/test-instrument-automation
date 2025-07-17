# Test Instrument Automation Framework

🚧 **This project is under active development and not yet ready for production use.**

This project provides a comprehensive framework for remotely controlling and automating test and measurement instruments. It features a modular architecture that separates instrument-specific logic from communication protocols, making it extensible and easy to maintain.

## Features

*   **Remote Instrument Control**: Communicate with and control GPIB-enabled instruments over an Ethernet network.
*   **Interactive Web UI**: A [Streamlit](https://streamlit.io/) application ([`streamlit.py`](d:\Programming\test-instrument-automation\streamlit.py)) provides a user-friendly interface for:
    *   Connecting to different instruments.
    *   Performing single measurements and sending basic commands.
    *   Visualizing live data with plots and tables.
*   **YAML-based Test Automation**: Use [OpenHTF](https://github.com/google/openhtf) to run automated test sequences defined in simple YAML files ([`scenario.yaml`](d:\Programming\test-instrument-automation\scenario.yaml)).
*   **Visual Scenario Builder**: A built-in tool ([`pages/scenario_builder.py`](d:\Programming\test-instrument-automation\pages\scenario_builder.py)) to graphically create and configure test scenarios, which can then be exported to YAML.
*   **Extensible Architecture**:
    *   **Adapter Pattern**: Easily switch between communication backends like Prologix GPIB-Ethernet ([`adapters/gpib_adapter.py`](d:\Programming\test-instrument-automation\adapters\gpib_adapter.py)) and PyVISA ([`adapters/pyvisa_adapter.py`](d:\Programming\test-instrument-automation\adapters\pyvisa_adapter.py)).
    *   **Device Drivers**: A clear structure for adding new instrument drivers, with existing implementations for the HP3458A DMM ([`devices/hp3458a.py`](d:\Programming\test-instrument-automation\devices\hp3458a.py)) and HP53131A Counter ([`devices/hp53131a.py`](d:\Programming\test-instrument-automation\devices\hp53131a.py)).

## Technologies Used

*   **Python**: Core programming language.
*   **Streamlit**: For the interactive web control panel and scenario builder.
*   **OpenHTF**: For running hardware test sequences.
*   **PyVISA**: As a backend for instrument communication.
*   **YAML & JSON Schema**: For defining and validating test scenarios.