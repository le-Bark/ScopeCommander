import win32com.client
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt

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