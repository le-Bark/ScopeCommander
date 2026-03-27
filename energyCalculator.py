import matplotlib.pyplot as plt
import math
from statistics import stdev, mean

class energyDataPoint():
    def __init__(self,index=0,value=0):
        self.index = index
        self.value = value
    voltage = 0
    current = 0

class energyCalculator():
    def __init__(self,time,voltage,current,currentMinus,integrationWindow):
        kernel = [1,2,3,4,5,6,5,4,3,2,1] 
        self.voltage = self.kernelSmooth(voltage,kernel)
        self.current = self.kernelSmooth(current,kernel)
        self.integrationWindow = integrationWindow
        if currentMinus != None:
            currentMinus = self.kernelSmooth(currentMinus,kernel)
            self.substractTraces(self.current,currentMinus)
        self.removeZeroOffset(self.current)
        self.result = {}
        self.time = time[0:len(self.voltage)]        
        

    def kernelSmooth(self,data,kernel):
        kernel = [1,2,3,4,5,6,5,4,3,2,1]
        sum = 0
        for i in kernel:
            sum += i

        smoothed = list(range(len(data)- len(kernel) + 1))
        for i, j in enumerate(smoothed):
            point = 0
            for k,l in zip(data[i:i+len(kernel)], kernel):
                point += k*l
            smoothed[i] = point / sum
        return smoothed

    def findZeroIndex(self,timeScale):
        lastj = timeScale[0]
        for i,j in enumerate(timeScale):
            if j == 0:
                return i
            elif lastj > 0 and j < 0:
                return i
            elif lastj < 0 and j > 0:
                return i
            lastj = j
        return math.ceil(len(timeScale) / 2)

    def findPlateau(self,data):
        oldstd = stdev(data)
        data = data [0:math.ceil(len(data) * .95)]
        newstd = stdev(data)
        stdChange = abs(oldstd-newstd)
        while(stdChange / newstd  > 0.05):
            oldstd = newstd
            data = data [0:math.ceil(len(data) * 0.9)]
            newstd = stdev(data)
            stdChange = abs(oldstd-newstd)
        return (mean(data),len(data))

    def removeZeroOffset(self,data):
        index5Percent = math.ceil(len(data) * 0.05)
        index95Percent = math.ceil(len(data) * 0.95)

        #scale current
        startOffset = 0 - mean(data[0:index5Percent])
        endOffset = 0 - mean(data[index95Percent:])
        offset = startOffset
        if abs(startOffset) > abs(endOffset):
            offset = endOffset
        for i in range(len(data)):
            data[i] = data[i] + offset

    # a = a - b
    def substractTraces(self,a,b):
        index5Percent = math.ceil(len(a) * 0.05)
        index95Percent = math.ceil(len(a) * 0.95)

        startOffset = mean((i-j for i,j in zip(a[0:index5Percent],b[0:index5Percent])))
        endOffset = mean((i-j for i,j in zip(a[index5Percent:],b[index95Percent:])))
        offset = startOffset
        if abs(startOffset) > abs(endOffset):
            offset = endOffset
        
        for i in range(len(a)):
            a[i] = a[i] - b[i] - offset

    def maxdxdt(self,data,dt,window,sign = 1):
        maxIndex = 0
        dxdtMax = 0
        for i in range(0,len(data)-window,1):
            dxdt = (data[i + window -1] - data[i]) / window / dt
            if sign * dxdt > dxdtMax:
                dxdtMax = sign * dxdt
                maxIndex = i
        return (maxIndex,sign*dxdtMax)

    def getMax(self,data):
        maxVal = data[0]
        index = 0
        for i,d in enumerate(data):
            if d>maxVal:
                maxVal = d
                index = i
        return (index,maxVal)

    #dir +1 / -1
    def get1090Index(self,data,bot,top,dir=1):
        index10 = 0
        index90 = 0
        for i,d in enumerate(data[::dir]):
            if index10 == 0:
                if d >= (top-bot) * 0.1:
                    index10 = i
            elif index90 == 0:
                if d >= (top-bot) * 0.9:
                    index90 = i
                    break
        if dir < 0:
            index10 = len(data) - 1 - index10
            index90 = len(data) - 1 - index90
        return (index10,index90)

    def integrate(self):        
        dt = self.time[1] - self.time[0]
        lastvi = self.voltage[self.integrationMin] * self.current[self.integrationMin]
        energy = 0
        for v,i in zip(self.voltage[1 + self.integrationMin:self.integrationMax],self.current[1 + self.integrationMin:self.integrationMax]):
            vi = v*i
            #energy += abs((vi + lastvi) * dt / 2)
            energy += (vi + lastvi) * dt / 2
            lastvi = vi
        return energy
    
    def calculate(self):
        if self.voltage[0] < self.voltage[-1]:
            #turn off
            self.turnOff()
        else:
            self.turnON()

    def turnON(self):
        index5P = math.ceil(len(self.time) * 0.05)
        index95P = math.ceil(len(self.time) * 0.95)
        dt = self.time[1] - self.time[0]

        #Vhigh / low (V)
        vHigh = energyDataPoint(index5P,mean(self.voltage[0:index5P]))
        vLow = energyDataPoint(index95P,mean(self.voltage[index95P:-1]))
        
        #vMax (V)
        vMax = energyDataPoint()
        vMax.index, vMax.value = self.getMax(self.voltage)

        #Overshoot (V)
        vOver = energyDataPoint()
        vOver.value = vMax.value - vHigh.value
        vOver.index = vMax.index

        #Rise / Fall time (ns)
        vIndex10p, vIndex90p = self.get1090Index(self.voltage,vLow.value,vHigh.value,-1)
        riseTime = energyDataPoint(int((vIndex10p + vIndex90p) / 2), self.time[vIndex10p] - self.time[vIndex90p])
        riseTime.value = riseTime.value * 1e9

        #max dV/dt (V / us)
        maxdvdt = energyDataPoint()
        maxdvdt.index, maxdvdt.value = self.maxdxdt(self.voltage[vIndex90p:vIndex10p],dt,10,-1)
        maxdvdt.index += vIndex90p
        maxdvdt.value = maxdvdt.value * 1e-6

        #I high / low(A)
        iHigh = energyDataPoint(index95P,mean(self.current[index95P:-1]))
        iLow = energyDataPoint(index5P,mean(self.current[0:index5P]))
        
        #I max (A)
        iMax = energyDataPoint()
        iMax.index,iMax.value = self.getMax(self.current)

        #dI/dt (V/us)
        iIndex10p, iIndex90p = self.get1090Index(self.current,iLow.value,iMax.value,1)
        maxdidt = energyDataPoint()
        maxdidt.index, maxdidt.value = self.maxdxdt(self.current[iIndex10p:iMax.index],dt,10,1)
        maxdidt.index += iIndex10p
        maxdidt.value = maxdidt.value * 1e-6

        #eOff (mj)
        integrationMin = (vIndex90p+vIndex10p) / 2 - abs(vIndex90p-vIndex10p) * self.integrationWindow/2
        integrationMax = (vIndex90p+vIndex10p) / 2 + abs(vIndex90p-vIndex10p) * self.integrationWindow/2
        self.integrationMin = int(max(0,integrationMin))
        self.integrationMax = int(min(integrationMax,len(self.voltage)-1))
        energy = energyDataPoint()
        energy.value = self.integrate() * 1e3        

        self.result = {
        "V max (V)" : vMax,
        "V high (V)" : vHigh,
        "Over / Undershoot (V)" : vOver,
        "Rise / Falltime (ns)" : riseTime,
        "dv / dt (V/us)" : maxdvdt,
        "I max (A)" : iMax,
        "dI /dt (A / us)" : maxdidt,
        "Itop (A)" : iHigh,
        "Energy (mJ)" : energy
        }
        for v in self.result.values():
            v.voltage = self.voltage[v.index]
            v.current = self.current[v.index]

    def turnOff(self):
        index5P = math.ceil(len(self.time) * 0.05)
        index95P = math.ceil(len(self.time) * 0.95)
        dt = self.time[1] - self.time[0]

        #Vhigh / low (V)
        vHigh = energyDataPoint(index95P,mean(self.voltage[index95P:-1]))
        vLow = energyDataPoint(index5P,mean(self.voltage[0:index5P]))
        
        #vMax (V)
        vMax = energyDataPoint()
        vMax.index, vMax.value = self.getMax(self.voltage)

        #Overshoot (V)
        vOver = energyDataPoint()
        vOver.value = vMax.value - vHigh.value
        vOver.index = vMax.index

        #Rise / Fall time (ns)
        vIndex10p, vIndex90p = self.get1090Index(self.voltage,vLow.value,vHigh.value,1)
        riseTime = energyDataPoint(int((vIndex10p + vIndex90p) / 2), self.time[vIndex90p] - self.time[vIndex10p])
        riseTime.value = riseTime.value * 1e9

        #max dV/dt (V / us)
        maxdvdt = energyDataPoint()
        maxdvdt.index, maxdvdt.value = self.maxdxdt(self.voltage[vIndex10p:vMax.index],dt,10,1)
        maxdvdt.index += vIndex10p
        maxdvdt.value = maxdvdt.value * 1e-6

        #I high / low(A)
        iHigh = energyDataPoint(index5P,mean(self.current[0:index5P]))
        iLow = energyDataPoint(index95P,mean(self.current[index95P:-1]))
        
        #I max (A)
        iMax = energyDataPoint()
        iMax.index,iMax.value = self.getMax(self.current)

        #dI/dt (V/us)
        iIndex10p, iIndex90p = self.get1090Index(self.current,iLow.value,iMax.value,-1)
        maxdidt = energyDataPoint()
        maxdidt.index, maxdidt.value = self.maxdxdt(self.current[iIndex90p:iIndex10p],dt,10,-1)
        maxdidt.index += iIndex90p
        maxdidt.value = maxdidt.value * 1e-6

        #eOff (mj)
        integrationMin = (vIndex90p+vIndex10p) / 2 - abs(vIndex90p-vIndex10p) * self.integrationWindow/2
        integrationMax = (vIndex90p+vIndex10p) / 2 + abs(vIndex90p-vIndex10p) * self.integrationWindow/2
        self.integrationMin = int(max(0,integrationMin))
        self.integrationMax = int(min(integrationMax,len(self.voltage)-1))
        energy = energyDataPoint()
        energy.value = self.integrate() * 1e3        

        self.result = {
        "V max (V)" : vMax,
        "V high (V)" : vHigh,
        "Over / Undershoot (V)" : vOver,
        "Rise / Falltime (ns)" : riseTime,
        "dv / dt (V/us)" : maxdvdt,
        "I max (A)" : iMax,
        "dI /dt (A / us)" : maxdidt,
        "Itop (A)" : iHigh,
        "Energy (mJ)" : energy
        }
        for v in self.result.values():
            v.voltage = self.voltage[v.index]
            v.current = self.current[v.index]
        
