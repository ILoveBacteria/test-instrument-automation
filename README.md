# Python-Based Test Automation Framework for Laboratory Instruments

🚧 **This project is under active development and not yet ready for production use.**

This project provides a comprehensive framework for remotely controlling and automating test and measurement instruments. It features a modular architecture that separates instrument-specific logic from communication protocols, making it extensible and easy to maintain.

## Technologies Used

-   **Python**: Core programming language.
-   **Streamlit**: For the interactive web control panel and scenario builder.
-   **PyVISA**: As a backend for instrument communication.
-   **Robot Framework**: For defining and executing test scenarios.
-   **Redis**: As a message broker for real-time updates and communication between components.
-   **PyMeasure**: For high-level instrument drivers.


## ✨ Key Features

- **Modular & Distributed Architecture**: Designed based on the [C4 model](https://github.com/ILoveBacteria/test-instrument-automation/tree/master/C4%20model), allowing components (GUI, Test Engine, Protocol Converter) to run on different systems.
- **Powerful Test Engine**: Utilizes [Robot Framework](https://github.com/robotframework/robotframework) to define and execute complex test scenarios, generate detailed reports, and manage test flows.
- **Interactive User Interface**: A web-based dashboard built with [Streamlit](https://streamlit.io/) for live control of instruments, test execution, and result visualization.
- **Standard Equipment Support**: Includes high-level drivers for common instruments like the HP-3458A Multimeter, HP-53131A Counter, and AFG-2225 Function Generator.
- **Flexible Communication Layer**: Supports both the commercial Prologix converter and a custom, low-cost GPIB converter based on a Raspberry Pi.
- **Real-time Monitoring**: Uses a message broker (Redis) to publish test execution events and instrument statuses live to the user interface.


## System Architecture

The system architecture is designed to be multi-layered and based on independent containers to provide maximum flexibility and extensibility. Below shows an overview of the main containers and their interactions:

1. **Streamlit GUI**: The web-based user interface for user interaction.

2. **Test Engine**: The core of the system, based on Robot Framework, which executes the scenarios.

3. **Test Event Broker**: A Redis message broker for asynchronous communication between the test engine and the UI.

4. **Pymeasure/PyVISA**: Abstraction layers to simplify communication with instruments.

5. **GPIB Converter**: The hardware converter (Prologix or Raspberry Pi) that translates commands to the GPIB protocol.


## 🔌 Supported Hardware

### Measurement Instruments

- HP 3458A Digital Multimeter
- HP 53131A Frequency Counter
- AFG-2225 Function Generator
- HP E4419B Power Meter

### GPIB Converters

- Prologix GPIB-Ethernet
- Custom Raspberry Pi-based converter (using the linux-gpib driver)

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Git
- A running Redis Server
- A Raspberry Pi with Raspberry Pi OS to use the custom converter.

### Installation & Setup

Clone the repository:

```bash
git clone [https://github.com/your-username/test-automation-framework.git](https://github.com/your-username/test-automation-framework.git)
cd test-automation-framework
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the proxy server (for network communication):

On the system connected to the instruments (e.g., the Raspberry Pi), run the [PyVISA-proxy](https://github.com/casabre/pyvisa-proxy) server:

```bash
python -m pyvisa_proxy --port 5000
```

### ⚙️ How to Use

Running the Graphical User Interface
To launch the web dashboard, run the following command:

```bash
streamlit run app.py
```

You can execute Robot Framework test scenarios directly from the user interface.

Here is a simple example of a test file (`measure_frequency.robot`) for measuring frequency:

```robot
*** Settings ***
Library    HP53131ALibrary.py      AS    Counter
Library    AFG2225Library.py       AS    Function

*** Test Cases ***
Measure 100kHz Frequency
    [Documentation]    Generate a 100kHz signal and measure it with the counter.
    
    # Establish connection via network proxy
    Counter.Open Connection       GPIB0::3::INSTR    visa_library=192.168.1.102:5000@proxy
    Function.Open Connection      ASRL5::INSTR
    
    # Configure Function Generator
    Function.Set Channel Frequency    1    100000
    Function.Set Channel Amplitude    1    1.0
    Function.Enable Channel Output    1
    
    # Measure and Validate
    Counter.Measure Frequency    channel=1
    ${freq}=    Counter.Initiate Wait And Fetch
    Should Be True    ${freq} > 99990 and ${freq} < 100010
    
    # Clean up
    Function.Close Connection
    Counter.Close Connection
```

## 🤝 Contributing

~~Contributions to this project are welcome! Please open a new issue to report bugs or suggest features, or submit a pull request with your changes.~~

Do **not** contribute yet, this project is still in early **development**.

## Interactive User Interface

A web-based dashboard built with [Streamlit](https://streamlit.io/) for live control of instruments, test execution, and result visualization.

### Screenshots

![Streamlit GUI Screenshot 1](https://github.com/ILoveBacteria/test-instrument-automation/blob/master/.github/assets/streamlit-gui-screenshot1.png)

![Streamlit GUI Screenshot 2](https://github.com/ILoveBacteria/test-instrument-automation/blob/master/.github/assets/streamlit-gui-screenshot2.png)
