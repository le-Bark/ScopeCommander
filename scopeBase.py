import pyvisa

class oscilloscope():
    def __init__(self,ipStr):
        self.rm = pyvisa.ResourceManager()
        self.ipStr = ipStr
        self.resourceStr = "TCPIP::{}::INSTR".format(self.ipStr)
        self.inst = None
        self.memDepth = 0
        self.data = {}
        self.activeChannels = []
        self.channels = []
        self.yScaleMin = 0
        self.yScaleMin = 256
        self.screenshotBuffer  = []
        

    def connect(self):
        try:
            self.inst = self.rm.open_resource(self.resourceStr,open_timeout=2000)
        except:
            return False
        return True

    def getActiveChannels(self):
        print("Not implemented")

    def getChannelsBuffer(self):
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