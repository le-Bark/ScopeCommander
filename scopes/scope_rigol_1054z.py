from scopeBase import oscilloscope
from scopeBase import dataScaler
from scopeBase import copyWidth

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
        self.maxDataTransfer = 250000
    
    def getActiveChannels(self):
        self.activeChannels = []
        for ch in self.channels:
            active = int(self.inst.query(":{}:DISP?".format(ch)))
            if active == 1:
                self.activeChannels.append(ch)
        return self.activeChannels

    def getChannelsBuffer(self,width=copyWidth.screenData):
        self.stop()
        self.data = {}
        self.scaledData = {}
        self.getActiveChannels()

        if width == copyWidth.fullBuffer:
            self.inst.write(":WAV:MODE RAW")
        else:
            self.inst.write(":WAV:MODE NORM") 

        preamble = []

        for ch in self.activeChannels:
            #todo : skip if mode is raw and channel is math
            #bug? if the traced is zoomed out in mormal mode, the full buffer is not transfered...
            self.inst.write(":WAV:SOUR {}".format(ch))
            self.inst.write(":WAV:FORM BYTE")
            preamble = self.inst.query(":WAV:PRE?").strip().split(",")
            points = int(preamble[2])
            yincr = float(preamble[7])
            yorigin = float(preamble[8])
            yref = float(preamble[9])
            self.data[ch] = [0] * points
            dataIndex = 0
            while points > self.maxDataTransfer:
                self.inst.write(":WAV:STAR {}".format(dataIndex+1))
                self.inst.write(":WAV:STOP {}".format(dataIndex+self.maxDataTransfer))
                self.data[ch][dataIndex:dataIndex+self.maxDataTransfer] = self.inst.query_binary_values(":WAV:DATA?", datatype='B')
                dataIndex += self.maxDataTransfer
                points -= self.maxDataTransfer
            if(points) > 0:
                self.inst.write(":WAV:STAR {}".format(dataIndex+1))
                self.inst.write(":WAV:STOP {}".format(dataIndex+points))
                self.data[ch][dataIndex:dataIndex+points] = self.inst.query_binary_values(":WAV:DATA?", datatype='B')

            self.scaledData[ch] = dataScaler(self.data[ch],yincr,(0-yorigin-yref)*yincr)

        points = int(preamble[2])
        xstep = float(preamble[4])
        xorigin = float(preamble[5])
        self.data["time"] = [i*xstep + xorigin for i in range(0,points)]
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

        
        