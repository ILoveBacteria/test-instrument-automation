import os
from enum import Enum

# 1) Define the enums/types your language uses

class Arg1Type(Enum):
    """Enumeration for the first argument of DVMSU."""
    MANUAL = "Manual"
    DC = "DC"
    AC_AC = "AC_ac"
    AC_DC = "AC_dc"
    RESISTANCE = "R(Resistance)"
    TRACK_HOLD_DELAY = "Track&Hold_Delay"
    TH = "T&H"

class ResistanceRange(Enum):
    """Enumeration for the second argument when arg1 is Resistance."""
    AUTO = "AUTO"
    R_100 = "100"
    R_1K = "1K"
    R_10K = "10K"
    R_100K = "100K"
    R_1MEG = "1Meg"
    R_10MEG = "10Meg"

class VoltageRange(Enum):
    """Enumeration for the second argument for non-resistance measurements."""
    AUTO = "AUTO"
    V_0_1 = 0.1
    V_1 = 1
    V_10 = 10
    V_100 = 100
    V_1000 = 1000

class Gain(Enum):
    """Enumeration for the third argument."""
    DB_30 = "30db"
    DB_80 = "80db"

class ErrorType(Enum):
    """Enumeration for the fourth argument (output)."""
    NO_ERR = "NO_Err"
    CALL_ERR = "Call_Err"
    RESPONSE_ERR = "Response_Err"
    OVF_ERR = "OVF_ERR"
    NETWORK_ERR = "Network_Err"
    INSTRUMENT_ERR = "Instrument_Err"


# 2) Define the commands

def DVMSU(arg1: Arg1Type, arg2, arg3: Gain, arg4: ErrorType):
    """
    Simulates the DVMSU command, validates inputs, and prints the execution details.

    Args:
        arg1: The primary measurement mode.
        arg2: The measurement range (voltage or resistance).
        arg3: The gain setting.
        arg4: The output error status (simulated).
    """
    print("-" * 40)
    print(f"Executing DVMSU with:")
    print(f"  arg1: {arg1.value} ({type(arg1)})")
    print(f"  arg2: {arg2.value if isinstance(arg2, Enum) else arg2} ({type(arg2)})")
    print(f"  arg3: {arg3.value} ({type(arg3)})")
    print(f"  arg4 (output): {arg4.value} ({type(arg4)})")

    # --- Input Validation ---
    if not isinstance(arg1, Arg1Type):
        raise TypeError(f"arg1 must be of type Arg1Type, but got {type(arg1)}")
    if not isinstance(arg3, Gain):
        raise TypeError(f"arg3 must be of type Gain, but got {type(arg3)}")
    if not isinstance(arg4, ErrorType):
        raise TypeError(f"arg4 must be of type ErrorType, but got {type(arg4)}")

    if arg1 == Arg1Type.RESISTANCE:
        if not isinstance(arg2, ResistanceRange):
            raise TypeError(f"For Resistance measurement, arg2 must be of type ResistanceRange, but got {type(arg2)}")
    else:
        if not isinstance(arg2, VoltageRange):
            raise TypeError(f"For non-Resistance measurement, arg2 must be of type VoltageRange, but got {type(arg2)}")

    # --- Command Logic (Simulation) ---
    print("\nValidation successful. Simulating command execution.")
    # In a real scenario, this is where you would interact with hardware.
    # The 'arg4' is an output, so in a real implementation, its value would be
    # determined by the function's outcome. Here we just print it.
    print(f"Simulated Result: The operation completed with status: {arg4.name}")
    print("-" * 40 + "\n")

program_filename = "program.dsl"
print(f"Created sample program file: '{program_filename}'")


# 4) Load & exec the "program" under a controlled namespace

dsl_globals = {
    # --- Commands ---
    "DVMSU": DVMSU,
    "print": print, # Allow printing for demonstration

    # --- Arg1Type ---
    "Manual": Arg1Type.MANUAL,
    "DC": Arg1Type.DC,
    "AC_ac": Arg1Type.AC_AC,
    "AC_dc": Arg1Type.AC_DC,
    "R_Resistance": Arg1Type.RESISTANCE, # Renamed to be a valid Python identifier
    "Track_Hold_Delay": Arg1Type.TRACK_HOLD_DELAY,
    "TH": Arg1Type.TH,

    # --- ResistanceRange ---
    "AUTO_R": ResistanceRange.AUTO, # Renamed to avoid conflict
    "R_100": ResistanceRange.R_100,
    "R_1K": ResistanceRange.R_1K,
    "R_10K": ResistanceRange.R_10K,
    "R_100K": ResistanceRange.R_100K,
    "R_1Meg": ResistanceRange.R_1MEG,
    "R_10Meg": ResistanceRange.R_10MEG,

    # --- VoltageRange ---
    "AUTO_V": VoltageRange.AUTO, # Renamed to avoid conflict
    "V_0_1": VoltageRange.V_0_1,
    "V_1": VoltageRange.V_1,
    "V_10": VoltageRange.V_10,
    "V_100": VoltageRange.V_100,
    "V_1000": VoltageRange.V_1000,

    # --- Gain ---
    "DB_30": Gain.DB_30,
    "DB_80": Gain.DB_80,

    # --- ErrorType (Output) ---
    "NO_Err": ErrorType.NO_ERR,
    "Call_Err": ErrorType.CALL_ERR,
    "Response_Err": ErrorType.RESPONSE_ERR,
    "OVF_ERR": ErrorType.OVF_ERR,
    "Network_Err": ErrorType.NETWORK_ERR,
    "Instrument_Err": ErrorType.INSTRUMENT_ERR,
}

# Execute the program from the file
try:
    with open(program_filename) as f:
        # We can filter out comment lines before executing
        code_lines = [line for line in f if not line.strip().startswith('#')]
        code = "".join(code_lines)
        exec(code, dsl_globals)
except Exception as e:
    print(f"\nAn error occurred during program execution: {e}")
