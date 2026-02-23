from scopeBase import oscilloscope
from scopeBase import dataScaler
from scopeBase import timeScale

class tek_MDO3X(oscilloscope):
    def __init__(self,ipStr):
        oscilloscope.__init__(self,ipStr)
        self.connect()
        self.inst.chunk_size = 102400
        self.channels = ["CH1","CH2","CH3","CH4"]
        self.yScaleMin = -128
        self.yScaleMax = 128

    def getActiveChannels(self):
        self.activeChannels = []
        for ch in self.channels:
            active = int(self.inst.query(":SEL:{}?".format(ch)))
            if active == 1:
                self.activeChannels.append(ch)
        return self.activeChannels

    def getChannelsBuffer(self):
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

            yMult = float(self.inst.query(":WFMOutpre:YMUlt?"))
            chPos = self.inst.query(":" + ch + ":pos?")
            chScale = self.inst.query(":" + ch + ":scal?")
            self.scaledData[ch] = dataScaler(self.data[ch],yMult,-float(chPos)*float(chScale))

        xZero = float(self.inst.query(":WFMOutpre:XZEro?"))
        xIncr = float(self.inst.query(":WFMOutpre:XINcr?"))
        self.data["time"] = [ xZero + i*xIncr for i in range(1,recordLength+1)]
        self.scaledData["time"] = self.data["time"]


    def single(self):
        self.inst.write(":ACQ:STATE RUN")
        self.inst.write(":ACQ:STOPA SEQ")

    def start(self):
        self.inst.write(":ACQ:STOPA RUNST")
        self.inst.write(":ACQ:STATE RUN")

    def stop(self):
        self.inst.write(":ACQ:STATE STOP")

    def takeScreenshot(self):
        if self.inst.query("FILESystem?").split(";")[0] == "\"\"":
            print("No usb flash drive!")
            raise ValueError('No flash drive!')
        self.inst.write("SAVE:IMAGe \"E:/temp.png\"")
        self.inst.query('*OPC?')
        self.inst.write("FILESystem:READFile \"E:/temp.png\"")
        self.screenshotBuffer = self.inst.read_raw()