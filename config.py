import os
import json


class controlConfig():
    def __init__(self,filename,defaultDict):
        self.filename = filename
        self.config = defaultDict

    def readConfig(self):
        if os.path.isfile(self.filename):
            f = open(self.filename,"r")
            readConfig = json.load(f)
            for k in readConfig.keys():
                if k in self.config.keys():
                    self.config[k] = readConfig[k]
    def writeConfig(self):
        f = open(self.filename,"w")
        json.dump(self.config,f)