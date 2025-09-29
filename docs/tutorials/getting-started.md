# 🚀 Getting Started

Welcome to the Test Instrument Automation documentation! This guide will help you set up your environment and get started with automating your test instruments using Python.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Docker**: For running the project in containers.
- **Python 3.10+**: If you prefer running the project locally.
- **Git**: To clone the repository.

## Option 1: Run with Docker

The easiest way to get started is by using Docker. Follow these steps:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/ILoveBacteria/test-instrument-automation.git
   cd test-instrument-automation
   ```

2. **Build and Start the Services**:
   ```bash
   docker-compose up --build
   ```

3. **Access the GUI**:
   Open your browser and navigate to [http://127.0.0.1:8501](http://127.0.0.1:8501).

4. **Verify Services**:
   - Redis: Runs in the background for message brokering.
   - Test Engine: Accessible via the GUI for running `.robot` test files.

## Option 2: Run Locally

If you prefer running the project locally, follow these steps:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/ILoveBacteria/test-instrument-automation.git
   cd test-instrument-automation
   ```

2. **Set Up a Python Virtual Environment**:
   Create and activate a virtual environment to isolate dependencies:

   ```bash
   pip install virtualenv
   ```

   - **On Windows**:
     ```bash
     python -m venv .venv
     .venv\Scripts\activate
     ```

   - **On macOS/Linux**:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Install Dependencies for Each Service**:
   Navigate to each service directory and install its requirements:

   - For the GUI:
     ```bash
     pip install -r gui/requirements.txt
     ```

   - For the Test Engine:
     ```bash
     pip install -r test_engine/requirements.txt
     ```

4. **Start Redis**:
   Ensure Redis is running locally. You can install it via your package manager or use Docker:
   ```bash
   docker run -d --name redis-server -p 6379:6379 redis:latest
   ```

5. **Run the Test Engine**:
   ```bash
   python test_engine/api_server.py
   ```

6. **Run the GUI**:
   ```bash
   streamlit run gui/live_dashboard.py
   ```

7. **Access the GUI**:
   Open your browser and navigate to [http://127.0.0.1:8501](http://127.0.0.1:8501).

## Next Steps

- Upload `.robot` files via the GUI to start running tests.
- Monitor test execution and device statuses in real-time.

Happy testing! 🎉

