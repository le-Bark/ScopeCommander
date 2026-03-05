import win32com.client
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt
from scopeBase import channelData, dataScaler

class excelCOM():
    def __init__(self):
        self.excel = None    
        self.workbookData = []
        self.selectedWorksheet = None
    def refresh(self):
        try:
            self.excel = win32com.client.GetActiveObject("Excel.Application")
            self.workbookData = []
            for wb in self.excel.Workbooks:
                self.workbookData.append({
                    "name": wb.name,
                    "worksheets": [(ws.name,ws) for ws in wb.Worksheets]
                })
        except:
            return False
        return True
    
    def generateTreeView(self):
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Excel Workbooks"])
        
        for wb in self.workbookData:
            workbook_item = QStandardItem(wb["name"])
            workbook_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            for ws_name,ws in wb["worksheets"]:
                worksheet_item = QStandardItem(ws_name)
                workbook_item.appendRow(worksheet_item)
                worksheet_item.setData(ws, Qt.ItemDataRole.UserRole)
                worksheet_item.setFlags(
                    Qt.ItemFlag.ItemIsEnabled |
                    Qt.ItemFlag.ItemIsSelectable
                )
            
            model.appendRow(workbook_item)
        
        return model
    
    def activateSelectedWorksheet(self):
        if self.selectedWorksheet != None:
            self.selectedWorksheet.Activate()

    def getRange(self,startCell,width,height):
        startCell = self.selectedWorksheet.Range(startCell)
        offsetCell = startCell.Offset(height,width)
        return self.selectedWorksheet.Range(startCell,offsetCell)
    
    def getNextFreeRange(self,startCell,width,height):
        range = self.getRange(startCell,width,height)
        while(not self.isRangeEmpty(range)):
            start = range.Cells(1).Offset(2,1)
            range = self.getRange(start.Address,width,height)
        return range

    def isRangeEmpty(self,range):
        for i in range.Value:
            for j in i:
                if j != None:
                    return False
        return True
    
    def importData(self,range):
        startCell = self.selectedWorksheet.Range("A1")
        if startCell.Value == None:
            return
        region = startCell.CurrentRegion
        excelData = region.Value
        header = list(excelData[0])
        data = channelData()
        dataLength = len(excelData) - 2
        data.channels = list(excelData[0][1:])
        for i,h in enumerate(header):
            if h == "time":
                data.time = [j[i] for j in excelData[2:]]
            else:
                data.raw[h] = [j[i] for j in excelData[2:]]
                data.scaled[h] = dataScaler(data.raw[h],1,0)
        return data
            
        
