import gpib


board = gpib.find("raspberry")
# Check if SRQ is asserted
if gpib.ibsta() & (1<<12):
    print('ibsta: ', "SRQ line is active!")
if gpib.lines(board) & 0x2000:
    print('lines: ', "SRQ line is active!")
