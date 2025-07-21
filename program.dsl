# This is a sample program file.
# Lines starting with # are comments and will be ignored by the parser.

print("--- Starting Program Execution ---")

# Example 1: DC Voltage Measurement
DVMSU(DC, V_10, DB_30, NO_Err)

# Example 2: Resistance Measurement
DVMSU(R_Resistance, R_1K, DB_80, NO_Err)

# Example 3: AC Voltage Measurement
DVMSU(AC_ac, AUTO_V, DB_30, NO_Err)

# Example 4: A call that might result in an error
DVMSU(Manual, V_100, DB_80, Call_Err)

# Example of an invalid call that will raise a TypeError
# DVMSU(DC, R_100, DB_30, NO_Err) # This would fail validation

print("--- Program Execution Finished ---")