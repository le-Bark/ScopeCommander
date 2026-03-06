import matplotlib.pyplot as plt
import math
from statistics import stdev, mean

class energyCalculator():
    def __init__(self,time,voltage,current,currentMinus=None):
        kernel = [1,2,3,4,5,6,5,4,3,2,1] 
        self.voltage = self.kernelSmooth(voltage,kernel)
        self.current = self.kernelSmooth(current,kernel)
        if currentMinus == None:
            self.currentMinus = None
        else:
            self.currentMinus = self.kernelSmooth(currentMinus,kernel)
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



    def integrateEdge(self):
        self.result = {}

        index5Percent = math.ceil(len(self.time) * 0.05)
        index2Percent = math.ceil(len(self.time) * 0.02)
        index95Percent = math.ceil(len(self.time) * 0.95)
        index98Percent = math.ceil(len(self.time) * 0.98)
        dt = self.time[1] - self.time[0]
        #scale voltage
        self.removeZeroOffset(self.voltage)
        #scale current
        if self.currentMinus != None:
            self.substractTraces(self.current,self.currentMinus)
        self.removeZeroOffset(self.current)

        maxV = (0,0)
        for i,v in enumerate(self.voltage):
            lasti,lastv = maxV
            if v > lastv:
                maxV = (i,v)
        minV = maxV
        for i,v in enumerate(self.voltage):
            lasti,lastv = minV
            if v < lastv:
                minV = (i,v)
        self.result["V max (V)"] = maxV


        t10p = 0
        t90p = 0
        v10p = 0
        v90p = 0
        lastv = 0
        maxdvdt = (0,0)
        if self.voltage[0] > self.voltage[-1]:
            Vhigh = (index5Percent,mean(self.voltage[0:index5Percent]))
            self.result["V high (V)"] = Vhigh
            self.result["Over / Undershoot (V)"] = minV
            for i,v in enumerate(self.voltage):
                if t10p == 0:
                    if v <= 0.1 * Vhigh[1]:
                        t10p = i
                        v10p = v
                elif i < minV[0]:
                    dvdt = (v-lastv) / dt
                    if dvdt < maxdvdt[1]:
                        maxdvdt = (i,dvdt)

                if t90p == 0:
                    if v <= 0.9 * Vhigh[1]:
                        t90p = i
                        v90p = v
                lastv = v
            self.result["Rise / Falltime (ns)"] = (int((t90p + t10p)/2), (self.time[t10p] - self.time[t90p]) * 1e9)
        
        else:
            Vhigh = (index95Percent,mean(self.voltage[index95Percent:]))
            self.result["V high (V)"] = Vhigh
            self.result["Over / Undershoot (V)"] = (maxV[0],maxV[1] - Vhigh[1])
            for i,v in enumerate(self.voltage):
                if t10p == 0:
                    if v >= 0.1 * Vhigh[1]:
                        t10p = i
                        v10p = v
                elif i < maxV[0]:
                    dvdt = (v-lastv) / dt
                    if dvdt > maxdvdt[1]:
                        maxdvdt = (i,dvdt)
                if t90p == 0:
                    if v >= 0.9 * Vhigh[1]:
                        t90p = i
                        v90p = v
                lastv = v
            self.result["Rise / Falltime (ns)"] = (int((t90p + t10p)/2), (self.time[t90p] - self.time[t10p]) * 1e9 )
        
        maxdvdt = (maxdvdt[0],maxdvdt[1] / 1e6)
        self.result["dv / dt (V/us)"] = maxdvdt

        maxI = (0,0)
        for i,I in enumerate(self.current):
            lasti,lastI = maxI
            if I > lastI:
                maxI = (i,I)
        self.result["I max (A)"] = maxI
        
        lastI = 0
        maxdidt = (0,0) 
        #turn ON
        if self.current[0] < self.current[-1]:
            Itop = (index95Percent,mean(self.current[index95Percent:]))
            for i,I in enumerate(self.current):
                if i > maxI[0]:
                    break
                if I >= Itop[1] * 0.1:
                    didt = (I - lastI) / dt
                    if didt > maxdidt[1]:
                        maxdidt = (i,didt)
                lastI = I
        #turn OFF
        else:
            Itop = (0,mean(self.current[0:index5Percent]))
            for i,I in enumerate(self.current):
                if i < Itop[0] * 0.1:
                    break
                if I <= Itop[1] * 0.9:
                    didt = (I - lastI) / dt
                    if didt < maxdidt[1]:
                        maxdidt = (i,didt)
                lastI = I

        self.result["dI /dt (A / us)"] = (maxdidt[0],maxdidt[1] / 1e6)
        self.result["Itop (A)"] = Itop 

        #integrate
        dt = self.time[1] - self.time[0]
        lastvi = self.voltage[0] * self.current[0]
        energy = 0
        for v,i in zip(self.voltage[1:],self.current[1:]):
            vi = v*i
            energy += abs((vi + lastvi) * dt / 2)
            lastvi = vi
        self.result["Energy (mJ)"] = (0,energy * 1000)
        

