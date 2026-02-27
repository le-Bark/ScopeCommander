import matplotlib.pyplot as plt
import math
from statistics import stdev, mean

class energyCalculator():
    def __init__(self):
        self.result = {}

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

    def integrateEdge(self,time,voltage,current):
        self.result = {}
        #smooth waveforms
        kernel = [1,2,3,4,5,6,5,4,3,2,1]
        vSmooth = self.kernelSmooth(voltage,kernel) 
        iSmooth = self.kernelSmooth(current,kernel)
        tSmooth = time[0:len(vSmooth)]

        #find voltage at begining  and at the end
        trigpoint = self.findZeroIndex(tSmooth)
        vStart, t = self.findPlateau(vSmooth[0:trigpoint])
        vStop, t = self.findPlateau(vSmooth[trigpoint:][::-1])
        print(time[::-1][t])
        plt.plot([time[::-1][t],time[-1]],[vStop,vStop])

        vBus = 0
        vZero = 0
        #turn off
        if vStart < vStop :
            iZero, t = self.findPlateau(iSmooth[trigpoint:][::-1])
            vZero = vStart
            vBus = vStop
            vSmooth = [i-vZero for i in vSmooth]
            iSmooth = [i-iZero for i in iSmooth]
        #turn on
        #else:
        #    iZero = findPlateau(iSmooth[0:trigpoint])
        #    vZero = vStop
        #    vBus = vStart
        
        self.result["I zero"] = iZero
        self.result["V start"] = vStart
        self.result["V stop"] = vStop

        #integrate
        dt = time[1] - time[0]
        lastvi = vSmooth[0] * iSmooth[0]
        energy = 0
        for v,i in zip(vSmooth[1:],iSmooth[1:]):
            vi = v*i
            energy += (vi + lastvi) * dt / 2
            lastvi = vi
        self.result["Energy"] = energy
        
        plt.plot(tSmooth,vSmooth)
        plt.plot(tSmooth,iSmooth)
        plt.show()










