import pyvisa
from enum import Enum

class copyWidth(Enum):
    screenData = 1
    fullBuffer = 2

class dataScaler():
    def __init__(self, data, factor, offset):
        self.data = data
        self.factor = float(factor)
        self.offset = float(offset)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.data[index] * self.factor + self.offset

    def __iter__(self):
        for item in self.data:
            yield item * self.factor + self.offset

class timeScale():
    def __init__(self, len, step, offset = 0):
        self.length = int(len)
        self.step = float(step)
        self.offset = float(offset)
    def __len__(self):
        return self.length
    def __getitem__(self, index):
        return index * self.step + self.offset
    def __iter__(self):
        for i in range(0,self.length):
            yield i * self.step + self.offset

class oscilloscope():
    def __init__(self,ipStr):
        self.rm = pyvisa.ResourceManager()
        self.ipStr = ipStr
        self.resourceStr = "TCPIP::{}::INSTR".format(self.ipStr)
        self.inst = None
        self.memDepth = 0
        self.data = {}
        self.scaledData = {}
        self.activeChannels = []
        self.channels = []
        self.yScaleMin = 0
        self.yScaleMin = 256
        self.screenshotBuffer  = []
        self.copyWidth = copyWidth.screenData
        

    def connect(self):
        try:
            self.inst = self.rm.open_resource(self.resourceStr,open_timeout=2000)
        except:
            return False
        return True

    def getActiveChannels(self):
        print("Not implemented")

    def getChannelsBuffer(self,copyWidth=copyWidth.screenData):
        print("Not implemented")

    def close(self):
        self.inst.close()

    def idn(self):
        idn = self.inst.query("*IDN?")
        return idn.strip()
    
    def single(self):
        print("Single not implemented")

    def start(self):
        print("Single not implemented")

    def stop(self):
        print("Single not implemented")
    def takeScreenshot(self):
        print("Single not implemented")