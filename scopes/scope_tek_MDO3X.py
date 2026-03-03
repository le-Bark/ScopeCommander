from scopeBase import oscilloscope
from scopeBase import dataScaler
from scopeBase import timeScale
from scopeBase import copyWidth

class tek_MDO3X(oscilloscope):
    def __init__(self,ipStr):
        oscilloscope.__init__(self,ipStr)

        self.channels = ["CH1","CH2","CH3","CH4","MATH"]
        self.yScaleMin = -128
        self.yScaleMax = 128
        self.connect()
        
        #self.inst.write(":SOCKETS:ENA ON")
        #self.inst.write(":SOCKETS:PORT 4000")
        #self.inst.write(":SOCKETS:PROTOC NON")
        #self.resourceStr = "TCPIP::{}::4000::SOCKET".format(ipStr)
        #self.connect()
        
        self.inst.write_termination = "\n"
        self.inst.read_termination = "\n"
        self.inst.timeout = 3000
        self.maxLabelLength = 30

    def getActiveChannels(self):
        self.inst.clear()
        self.activeChannels = []
        for ch in self.channels:
            self.inst.write("DAT:SOU {}".format(ch))
            header = self.inst.query("WFMOutpre?").strip().split(";")
            if(len(header) > 5):
                self.activeChannels.append(ch)
        return self.activeChannels

    def getChannelsBuffer(self,width=copyWidth.screenData):
        self.inst.clear()
        self.stop()
        self.data = {}
        self.scaledData = {}
        self.getActiveChannels()
        
        recordLength = int(self.inst.query(":HOR:RECO?"))

        for ch in self.activeChannels:
            self.inst.write("DAT:SOU " + ch)
            self.inst.write("DAT:STAR 1")
            self.inst.write("DAT:STOP {}".format(recordLength))
            self.inst.write(":WFMInpre:BYT_Nr 1")
            self.inst.write(":HEADer 0")
            self.inst.write(":WFMInpre:ENCdg BIN")

            self.data[ch] = self.inst.query_binary_values('CURV?', datatype='b')

            header = self.inst.query("WFMOutpre?").strip().split(";")
            scale = float(header[14])
            offset = float(header[15])
            self.scaledData[ch] = dataScaler(self.data[ch],scale,-offset*scale)

        xZero = float(self.inst.query(":WFMOutpre:XZEro?"))
        xIncr = float(self.inst.query(":WFMOutpre:XINcr?"))
        self.data["time"] = [ xZero + i*xIncr for i in range(1,recordLength+1)]
        self.scaledData["time"] = self.data["time"]


    def single(self):
        self.inst.clear()
        self.inst.write(":ACQ:STATE RUN")
        self.inst.write(":ACQ:STOPA SEQ")

    def start(self):
        self.inst.clear()
        self.inst.write(":ACQ:STOPA RUNST")
        self.inst.write(":ACQ:STATE RUN")

    def stop(self):
        self.inst.clear()
        self.inst.write(":ACQ:STATE STOP")

    def takeScreenshot(self):
        self.inst.clear()
        if self.inst.query("FILESystem?").split(";")[0] == "\"\"":
            print("No usb flash drive!")
            raise ValueError('No flash drive!')
        self.inst.write("SAVE:IMAGe \"E:/temp.png\"")
        self.inst.query('*OPC?')
        self.inst.write("FILESystem:READFile \"E:/temp.png\"")
        self.screenshotBuffer = self.inst.read_raw()

    def getChannelLabels(self):
        self.inst.clear()
        for ch in self.channels:
            enabled = 0 #not supported
            label = self.inst.query(":{}:lab?".format(ch)).replace("\"","")
            self.labels[ch] = (enabled,label)
        return self.labels
    
    def setChannelLabel(self,ch,enabled,label):
        self.inst.clear()
        self.inst.write(":{}:lab \"{}\"".format(ch,label))
        return self.labels