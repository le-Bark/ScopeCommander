from scopeBase import oscilloscope
from scopeBase import dataScaler

class rigol_1054z(oscilloscope):
    def __init__(self,ipStr):
        oscilloscope.__init__(self,ipStr)
        self.resourceStr = "TCPIP::{}::5555::SOCKET".format(self.ipStr)
        self.connect()
        self.inst.write_termination = "\r\n"
        self.inst.read_termination = "\n"
        self.inst.chunk_size = 102400
        self.channels = ["CHAN1","CHAN2","CHAN3","CHAN4"]
        self.yScaleMin = 0
        self.yScaleMax = 256
    

    def getActiveChannels(self):
        self.activeChannels = []
        for ch in self.channels:
            active = int(self.inst.query(":{}:DISP?".format(ch)))
            if active == 1:
                self.activeChannels.append(ch)
        return self.activeChannels

    def getChannelsBuffer(self):
        self.stop()
        self.data = {}
        self.scaledData = {}
        self.getActiveChannels()
        self.inst.write(":WAV:MODE NORM")
        self.inst.write(":WAV:FORM BYTE")
        stop = int(self.inst.query(":WAV:STOP?"))
        xstep = float(self.inst.query(":WAV:XINC?"))
        
        preamble = self.inst.query(":WAV:PRE?").strip().split(",")
        points = int(preamble[2])

        self.inst.write(":WAV:STAR 1")
        self.inst.write(":WAV:STOP {}".format(points))

        for ch in self.activeChannels:
            self.inst.write(":WAV:SOUR {}".format(ch))            
            incr = float(self.inst.query(":WAV:YINC?"))
            yorigin = float(self.inst.query(":WAVeform:YOR?"))
            yref = float(self.inst.query(":WAVeform:YREF?"))
            self.data[ch] = self.inst.query_binary_values(":WAV:DATA?", datatype='B')
            self.scaledData[ch] = dataScaler(self.data[ch],incr,(0-yorigin-yref)*incr)

        self.data["time"] = [i*xstep for i in range(0,stop)]
        self.scaledData["time"] = self.data["time"]

    def single(self):
        self.inst.write(":SING")

    def start(self):
        self.inst.write(":RUN")

    def stop(self):
        self.inst.write(":STOP")
    
    def takeScreenshot(self):
        self.inst.write(":DISP:DATA? ON OFF PNG")
        values = self.inst.read_raw()
        headerLength = int(chr(values[1]))
        imageSize = int("".join([chr(i) for i in values[2:2+headerLength]]))
        self.screenshotBuffer = values[2+headerLength:2+headerLength+imageSize]

        
        