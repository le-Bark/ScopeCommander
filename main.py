from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import sys
import mainWindow
import scopeBase
from scopes.scope_rigol_1054z import rigol_1054z
from scopes import scopeCompatibility
from config import controlConfig
import excelCom

app = QApplication(sys.argv)

class scopeCommander(QMainWindow, mainWindow.Ui_MainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.ax = self.GraphWidget.canvas.ax

        self.topTabWidget.setCurrentIndex(0)
        self.bottomTabWidget.setCurrentIndex(0)

        self.connectButton.clicked.connect(self.onConnect)
        self.copyDataButton.clicked.connect(self.onCopy)
        self.screenCaptureButton.clicked.connect(self.onScreenCapture)
        self.saveClipboardButton.clicked.connect(self.onSavetoClipboard)
        self.excelRefreshButton.clicked.connect(self.onExcelRefresh)
        self.excelExportButton.clicked.connect(self.onExcelExport)

        self.scope = None
        self.pixmap = None
        defaultConfig = {"ip":""}
        self.configReader = controlConfig("config.json",defaultConfig)
        self.configReader.readConfig()
        self.ipInput.setText(self.configReader.config["ip"])

        self.screenCaptureLabel.setText("")

        #self.excelCom = excelCom.excelCOM()
        self.excelCom = None


    def onConnect(self):
        ipStr = self.ipInput.text().strip()
        self.configReader.config["ip"] = ipStr
        self.configReader.writeConfig()
        self.idnDisplay.clear()
        if self.scope != None:
            self.unlinkScope()

        self.scope = scopeBase.oscilloscope(ipStr)
        
        if self.scope.connect():
            self.idnDisplay.setText(self.scope.idn())
            self.scope = scopeCompatibility.getCompatibleClass(self.scope)
            if self.scope == None:
                self.idnDisplay.setText("Scope not compatible")
            else:
                self.linkScope()
        else:
            self.idnDisplay.setText("connection failed")
            self.scope = None
    
    def linkScope(self):
        self.singleTrigButton.clicked.connect(self.scope.single)
        self.startButton.clicked.connect(self.scope.start)
        self.stopButton.clicked.connect(self.scope.stop)
        self.copyDataButton.setEnabled(True)
        self.screenCaptureButton.setEnabled(True)

    def unlinkScope(self):
        self.singleTrigButton.clicked.disconnect(self.scope.single)
        self.startButton.clicked.disconnect(self.scope.start)
        self.stopButton.clicked.disconnect(self.scope.stop)
        self.copyDataButton.setEnabled(False)
        self.scope.close()
        self.scope = None
        self.idnDisplay.setText("Disconnected")


    def onCopy(self):
        self.scope.getChannelsBuffer()
        self.GraphWidget.canvas.ax.cla()
        for ch in self.scope.activeChannels:
            self.ax.plot(self.scope.data["time"],self.scope.data[ch])
        self.ax.set_ylim(self.scope.yScaleMin,self.scope.yScaleMax)
        self.ax.set_xlim(self.scope.data["time"][0],self.scope.data["time"][-1])
        for line in self.ax.get_lines():
            line.set_linewidth(1)
        self.GraphWidget.canvas.draw()

    def onScreenCapture(self):
        self.scope.takeScreenshot()
        self.pixmap = QPixmap()
        self.pixmap.loadFromData(self.scope.screenshotBuffer)
        self.screenCaptureLabel.setPixmap(self.pixmap)
    def onSavetoClipboard(self):
        #pixmap = self.GraphWidget.canvas.grab()
        if self.pixmap != None:
            QApplication.clipboard().setPixmap(self.pixmap)

    def onExcelRefresh(self):
        if self.excelCom == None:
            self.excelCom = excelCom.excelCOM()
        self.excelCom.refresh()
        print(self.excelCom.workbookData)
        self.excelTreeView.setModel(self.excelCom.generateTreeView())
        self.excelTreeView.selectionModel().selectionChanged.connect(self.onExcelTreeSelectionChanged)
    
    def onExcelTreeSelectionChanged(self,selected, deselected):
        indexes = selected.indexes()
        if not indexes:
            self.excelCom.selectedWorksheet = None
            self.excelExportButton.setEnabled(False)
            return
        index = indexes[0]
        self.excelCom.selectedWorksheet = index.data(Qt.ItemDataRole.UserRole)
        self.excelCom.activateSelectedWorksheet()
        self.excelExportButton.setEnabled(True)
    
    def onExcelExport(self):
        if self.scope == None:
            return
        if self.scope.data == {}:
            return
        #set header
        sheet = self.excelCom.selectedWorksheet 
        range = sheet.Range(
            sheet.Cells(1, 1),
            sheet.Cells(1, len(self.scope.activeChannels) + 1))
        range.Value = ["time"] + self.scope.activeChannels
        for i,ch in enumerate(["time"] + self.scope.activeChannels):
            range = sheet.Range(
                sheet.Cells(2, i+1),
                sheet.Cells(2+len(self.scope.scaledData[ch]) - 1, i+1))
            range.Value = [[i] for i in self.scope.scaledData[ch]]
        



window = scopeCommander()
window.show()

app.exec()