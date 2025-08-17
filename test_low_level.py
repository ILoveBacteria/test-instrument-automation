# import gpib
from Gpib import Gpib


gpib = Gpib(0, 3)
# g = Gpib(name=0)
gpib.write("*IDN?")
response = gpib.read(100)
print("Device says:", response)
