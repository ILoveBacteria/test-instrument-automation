# NI Teststand API

## The Order of Code Generation

1. `test_engine.py`
2. `test_sequence.py`
3. `test_execution.py`
4. `test_parse_result.py`

## Outputs

`test_engine.py`

Successfully connected to TestStand Engine version: 24.0

`test_sequence.py`

Successfully connected to TestStand Engine version: 24.0
Successfully loaded sequence file: C:\Users\Mohammad Moein\Documents\hello.seq
Sequence file released.

`test_execution.py`

Successfully connected to TestStand Engine version: 24.0
Successfully loaded sequence file: C:\Users\Mohammad Moein\Documents\hello.seq
Launched direct execution of MainSequence.
Waiting for execution to complete...
Execution finished. ResultStatus: Passed
Sequence file released.

## How to run

The `pywin32` library is the essential bridge that enables Python to communicate with Windows COM objects, including the TestStand Engine.

```sh
pip install pywin32
```

the bitness of the Python interpreter must match the bitness of the installed TestStand application.

- A 32-bit Python interpreter can only interface with a 32-bit TestStand installation.
- A 64-bit Python interpreter can only interface with a 64-bit TestStand installation.

## Best Practice

### Using Context Managers (with statements) for Automatic Resource Release

The complex `try...finally` blocks required for robust cleanup can be elegantly encapsulated using Python's context manager protocol (`with` statements). A custom class can be written to handle the acquisition and, more importantly, the guaranteed release of the TestStand Engine.

The following example demonstrates a context manager for the TestStand Engine:

```python
import win32com.client
import pythoncom

class TestStandEngineManager:
    def __init__(self):
        self.engine = None

    def __enter__(self):
        # This is called at the start of the 'with' block
        try:
            self.engine = win32com.client.Dispatch("TestStand.Engine.1")
            # Enable message polling for shutdown
            self.engine.UIMessagePollingEnabled = True
            return self.engine
        except Exception as e:
            print(f"Failed to initialize TestStand Engine: {e}")
            raise

    def __exit__(self, exc_type, exc_value, traceback):
        # This is always called at the end of the 'with' block,
        # even if exceptions occur.
        if self.engine:
            print("Shutting down TestStand Engine...")
            self.engine.ShutDown(True) # True to shut down even if in use
            
            # Poll for shutdown complete message
            while True:
                msg = self.engine.GetUIMessage(0x1) # UIMsg_ShutDownComplete is 9
                if msg:
                    if msg.Event == 9: # UIMsg_ShutDownComplete
                        print("Shutdown complete message received.")
                        break
                pythoncom.PumpWaitingMessages() # Process messages
            
            self.engine = None
            print("Engine reference released.")
```

Using this class makes the main script clean and ensures that the complex shutdown procedure is always executed:

```python
with TestStandEngineManager() as ts_engine:
    # All API calls using ts_engine happen here.
    # Cleanup is automatically handled on exit from the 'with' block.
    print("Engine is active within the 'with' block.")
```

## Conclusion

For any organization planning to make extensive use of this Python-TestStand integration, investing time in building a shared, internal wrapper library is a critical step. Such a library would encapsulate the try...except...finally logic, the WithEvents event handling, and the context manager patterns. It would expose a simplified, robust, and Pythonic interface (e.g., `engine.execution_and_get_results(path)`) that handles the complex and error-prone COM interactions internally.