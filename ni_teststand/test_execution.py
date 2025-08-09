import win32com.client
import sys

try:
    # Use the version-specific ProgID for reliability
    # The version number may vary depending on the TestStand installation
    ts_engine = win32com.client.Dispatch("TestStand.Engine.1") 
    print(f"Successfully connected to TestStand Engine version: {ts_engine.MajorVersion}.{ts_engine.MinorVersion}")
    
    # Assuming ts_engine is a valid Engine object from Section 2.5
    seq_file_path = "C:\\Users\\Public\\Documents\\National Instruments\\TestStand 2021 (64-bit)\\Examples\\TestStand API\\Executing Sequences Using API\\TestStand Expressions\\Target Sequence File.seq"
    seq_file = None
    try:
        seq_file = ts_engine.GetSequenceFileEx(seq_file_path)
        print(f"Successfully loaded sequence file: {seq_file.Path}")
        
        #... sequence execution logic will go here...
        # To run the "MainSequence" directly, without a process model
        execution = ts_engine.NewExecution(seq_file, "MainSequence", None, False, 0)
        print("Launched direct execution of MainSequence.")
        #... after calling ts_engine.NewExecution(...)
        print("Waiting for execution to complete...")
        # Wait for up to 60 seconds (60000 ms)
        result = execution.WaitForEndEx(60000) 
        print(f"Execution finished. ResultStatus: {execution.ResultStatus}")
    finally:
        if seq_file:
            ts_engine.ReleaseSequenceFileEx(seq_file)
            print("Sequence file released.")
            seq_file = None # Best practice to clear the Python variable

except Exception as e:
    print(f"Failed to connect to TestStand Engine: {e}")
    # Check for architecture mismatch
    print(f"Python architecture: {sys.maxsize > 2**32 and '64-bit' or '32-bit'}")
    print("Ensure Python architecture matches TestStand installation architecture.")
