import win32com.client
import sys

try:
    # Use the version-specific ProgID for reliability
    # The version number may vary depending on the TestStand installation
    ts_engine = win32com.client.Dispatch("TestStand.Engine.1") 
    print(f"Successfully connected to TestStand Engine version: {ts_engine.MajorVersion}.{ts_engine.MinorVersion}")

except Exception as e:
    print(f"Failed to connect to TestStand Engine: {e}")
    # Check for architecture mismatch
    print(f"Python architecture: {sys.maxsize > 2**32 and '64-bit' or '32-bit'}")
    print("Ensure Python architecture matches TestStand installation architecture.")
