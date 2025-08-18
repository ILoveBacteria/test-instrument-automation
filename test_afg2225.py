import pyvisa
from devices import AFG2225


def visa():
    rm = pyvisa.ResourceManager()
    inst = rm.open_resource("ASRL5::INSTR")
    print(inst.query("*IDN?"))


def pymeasure():
    device = AFG2225("ASRL5::INSTR")
    print(device.id)
    

if __name__ == '__main__':
    visa()
    pymeasure()
