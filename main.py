from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QTableWidgetItem
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtWidgets import QMessageBox, QHeaderView
import sys
import mainWindow
import scopeBase
from scopes.scope_rigol_1054z import rigol_1054z
from scopes import scopeCompatibility
from config import controlConfig
import excelCom
from tracePlot import graphTab
from energyCalculator import energyCalculator

app = QApplication(sys.argv)

class scopeCommander(QMainWindow, mainWindow.Ui_MainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.ax = self.GraphWidget.canvas.ax
        self.energyGraphTab = None
        self.topTabWidget.setCurrentIndex(0)
        self.bottomTabWidget.setCurrentIndex(0)

        self.connectButton.clicked.connect(self.onConnect)
        self.copyDataButton.clicked.connect(self.onCopy)
        self.screenCaptureButton.clicked.connect(self.onScreenCapture)
        self.saveClipboardButton.clicked.connect(self.onSavetoClipboard)
        self.excelRefreshButton.clicked.connect(self.onExcelRefresh)
        self.excelExportButton.clicked.connect(self.onExcelExport)
        self.toExcelButton.clicked.connect(self.onToExcel)
        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(False)
        self.singleTrigButton.setEnabled(False)

        self.importButton.clicked.connect(self.onExcelImport)
        self.calculateEnergyButton.clicked.connect(self.onCalculateEnergy)
        self.scope = None
        self.pixmap = None
        defaultConfig = {"ip":""}
        self.configReader = controlConfig("config.json",defaultConfig)
        self.configReader.readConfig()
        self.ipInput.setText(self.configReader.config["ip"])

        self.screenCaptureLabel.setText("")

        #self.excelCom = excelCom.excelCOM()
        self.excelCom = None
        self.data = scopeBase.channelData()


    def channelTableSetup(self):
        tab = self.ChannelTable
        tab.clearContents()
        tab.setColumnCount(2)
        tab.setRowCount(len(self.scope.channels))
        tab.setHorizontalHeaderLabels(["Channel", "Label"])
        #tab.horizontalHeader().setStretchLastSection(True)
        tab.verticalHeader().setVisible(False)
        tab.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        tab.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        tab.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents)
        tab.horizontalHeader().setSectionResizeMode(1,QHeaderView.Stretch)
        try:
            tab.cellChanged.connect(self.onChannelListItemChange,type=Qt.UniqueConnection)        
        except:
            pass
        self.updateChannelTable()

    def updateChannelTable(self):
        
        try:
            self.scope.getChannelLabels()
        except:
            self.unlinkScope()
            return

        self.ChannelTable.blockSignals(True)
        for row,ch in enumerate(self.scope.labels.keys()): #to set label eventually
            enabled,label = self.scope.labels[ch]
            chItem = QTableWidgetItem(ch)
            chItem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.ChannelTable.setItem(row, 0, chItem)

            lableItem = QTableWidgetItem(label)
            lableItem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
            lableItem.setCheckState([Qt.Unchecked,Qt.Checked][int(enabled)])
            self.ChannelTable.setItem(row, 1, lableItem)
        self.ChannelTable.blockSignals(False)

    def onConnect(self):
        ipStr = self.ipInput.text().strip()
        self.configReader.config["ip"] = ipStr
        self.configReader.writeConfig()
        self.idnDisplay.clear()
        if self.scope != None:
            self.unlinkScope()

        self.scope = scopeBase.oscilloscope(ipStr)
        #self.linkScope()

        if self.scope.connect():
            try:
                self.idnDisplay.setText(self.scope.idn())
            except:
                return
            self.scope = scopeCompatibility.getCompatibleClass(self.scope)
            if self.scope == None:
                self.idnDisplay.setText("Scope not compatible")
            else:
                self.linkScope()
        else:
            self.idnDisplay.setText("connection failed")
            self.scope = None
    
    def linkScope(self):
        self.singleTrigButton.clicked.connect(self.onSingle)
        self.startButton.clicked.connect(self.onStart)
        self.stopButton.clicked.connect(self.onStop)
        self.copyDataButton.setEnabled(True)
        self.screenCaptureButton.setEnabled(True)
        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(True)
        self.singleTrigButton.setEnabled(True)
        self.channelTableSetup()

    def unlinkScope(self):
        self.singleTrigButton.clicked.disconnect(self.onSingle)
        self.startButton.clicked.disconnect(self.onStart)
        self.stopButton.clicked.disconnect(self.onStop)
        self.copyDataButton.setEnabled(False)
        self.screenCaptureButton.setEnabled(False)
        self.scope.close()
        self.scope = None
        self.idnDisplay.setText("Disconnected")
        self.ChannelTable.clearContents()
        self.ChannelTable.disconnect()
        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(False)
        self.singleTrigButton.setEnabled(False)

    def onChannelListItemChange(self,row,column):
        item = self.ChannelTable.item(row,column)
        if len(item.text()) > self.scope.maxLabelLength:
            item.setText(item.text()[0:self.scope.maxLabelLength])
        if self.scope != None:
            ch = self.ChannelTable.item(row,0).text()
            label = item.text()
            enabled = int(not not item.checkState())
        try:
            self.scope.setChannelLabel(ch,enabled,label)
            self.scope.getChannelLabels()
        except:
            self.unlinkScope()
            return
        self.updateChannelTable()

    def onCopy(self):
        self.topTabWidget.setCurrentIndex(0)
        try:
            self.scope.getChannelsBuffer()
        except ValueError as err:
            QMessageBox.critical(None, "Error", "-".join(err.args))
            return
        except:
            self.unlinkScope()
            return
        self.GraphWidget.canvas.ax.cla()
        self.data = self.scope.data
        if len(self.data) == 0:
            return
        for ch in self.data.channels:
            self.ax.plot(self.data.time,self.data.raw[ch])
        self.ax.set_ylim(self.scope.yScaleMin,self.scope.yScaleMax)
        self.ax.set_xlim(self.data.time[0],self.data.time[-1])
        for line in self.ax.get_lines():
            line.set_linewidth(1)
        self.GraphWidget.canvas.draw()

    def onScreenCapture(self):
        self.topTabWidget.setCurrentIndex(1)
        try:
            self.scope.takeScreenshot()
        except ValueError as err:
            QMessageBox.critical(None, "Error", "-".join(err.args))
            return
        except:
            self.unlinkScope()
            return
        
        self.pixmap = QPixmap()
        self.pixmap.loadFromData(self.scope.screenshotBuffer)        
        self.screenCaptureLabel.setPixmap(self.pixmap)
        self.screenCaptureLabel.setScaledContents(True)
    
    def onSavetoClipboard(self):
        if self.pixmap != None:
            QApplication.clipboard().setPixmap(self.pixmap)

    def onToExcel(self):
        self.onSavetoClipboard()
        sheet = self.excelTreeView.selectedIndexes()[0].data(Qt.ItemDataRole.UserRole)
        self.excelCom.selectedWorksheet = sheet
        if self.screenCaptureLabel.pixmap() is not None:
            sheet.Range("G2").Select()
            sheet.Paste()
            img = sheet.Shapes(sheet.Shapes.Count)
            img.LockAspectRatio = True
            img.Width = 300

    def onExcelRefresh(self):
        if self.excelCom == None:
            self.excelCom = excelCom.excelCOM()
        self.excelCom.refresh()
        self.excelTreeView.setModel(self.excelCom.generateTreeView())
        self.excelTreeView.expandAll()
        self.excelTreeView.selectionModel().selectionChanged.connect(self.onExcelTreeSelectionChanged)
    
    def onExcelTreeSelectionChanged(self,selected, deselected):
        indexes = selected.indexes()
        if not indexes:
            self.excelCom.selectedWorksheet = None
            self.excelExportButton.setEnabled(False)
            self.toExcelButton.setEnabled(False)
            return
        index = indexes[0]
        self.excelCom.selectedWorksheet = index.data(Qt.ItemDataRole.UserRole)
        self.excelCom.activateSelectedWorksheet()
        self.excelExportButton.setEnabled(True)
        self.toExcelButton.setEnabled(True)
    
    def channelDataToExcelFormat(self):
        fields = self.data.channels
        length = len(self.data)
        for i in range(0,length):
            yield [self.data.time[i]] + [self.data.scaled[f][i] for f in fields]
    
    def onExcelExport(self):
        if len(self.data) == 0:
            return
        #set header
        sheet = self.excelTreeView.selectedIndexes()[0].data(Qt.ItemDataRole.UserRole)
        self.excelCom.selectedWorksheet = sheet
        range = self.excelCom.getRange("A1",len(self.data.channels)+1,1)
        rangeFree = True
        for i in range.Value[0]:
            if i != None:
                rangeFree = False
        if rangeFree == False:
            reply = QMessageBox.question(
                window,
                "Overwrite data?",
                "Overwrite the existing data?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No  # bouton par défaut
                )
            if reply == QMessageBox.No:
                return
        
        range.Value = ["time"] + self.data.channels
        if self.scope != None:
            if self.scope.labels != {}:
                range = self.excelCom.getRange("B2",len(self.scope.activeChannels),1)
                range.Value = [self.scope.labels[ch][1] for ch in self.scope.activeChannels]
        sheet.Range("A2").Value = "Labels ->"
        range = self.excelCom.getRange("A3",1+len(self.data.channels),len(self.data))
        range.Value = list(self.channelDataToExcelFormat())
        
    def onExcelImport(self):
        self.data = scopeBase.channelData()
        self.data = self.excelCom.importData("A1")
        self.GraphWidget.canvas.ax.cla()
        
        for ch in self.data.channels:
            self.ax.plot(self.data.time,self.data.scaled[ch])
        #self.ax.set_ylim(self.scope.yScaleMin,self.scope.yScaleMax)
        #self.ax.set_xlim(self.data["time"][0],self.data["time"][-1])
        for line in self.ax.get_lines():
            line.set_linewidth(1)
        self.GraphWidget.canvas.draw()
        self.updateEnergyGUI()
        

    def onStop(self):
        try:
            self.scope.stop()
        except:
            self.unlinkScope()
    def onStart(self):
        try:
            self.scope.start()
        except:
            self.unlinkScope()
    def onSingle(self):
        try:
            self.scope.single()
        except:
            self.unlinkScope()

    def updateEnergyGUI(self):
        self.energyVoltageComboBox.clear()
        self.energyCurrentcomboBox.clear()
        self.energyCurrentcomboBoxMinus.clear()
        self.energyCurrentcomboBoxMinus.addItem("0")
        for ch in self.data.channels:
            self.energyVoltageComboBox.addItem(ch)
            self.energyCurrentcomboBox.addItem(ch)
            self.energyCurrentcomboBoxMinus.addItem(ch)
        self.calculateEnergyButton.setEnabled(True)
        
    def onCalculateEnergy(self):
        if self.energyGraphTab == None:
            self.energyGraphTab = graphTab(self.topTabWidget)
            self.topTabWidget.addTab(self.energyGraphTab, "Energy graph")
            ax1 = self.energyGraphTab.GraphWidget.canvas.ax
            self.energyGraphTab.GraphWidget.canvas.ax2 = ax1.twinx()
        self.topTabWidget.setCurrentIndex(2)
        V = self.data.scaled[self.energyVoltageComboBox.currentText()]
        I = self.data.scaled[self.energyCurrentcomboBox.currentText()]
        Iminus = None
        IminusChannel = self.energyCurrentcomboBoxMinus.currentText()
        if IminusChannel != "0":
            Iminus = self.data.scaled[IminusChannel]
        self.energyCalculator = energyCalculator(self.data.time,V,I,Iminus)

        fig = self.energyGraphTab.GraphWidget.canvas.fig
        ax1 = self.energyGraphTab.GraphWidget.canvas.ax
        ax2 = self.energyGraphTab.GraphWidget.canvas.ax2
        ax1.cla()
        ax2.cla()

        self.energyCalculator.integrateEdge()

        ax1.plot(self.energyCalculator.time,self.energyCalculator.voltage)
        ax2.plot(self.energyCalculator.time,self.energyCalculator.current)
        #if self.energyCalculator.currentMinus != None:
        #    ax2.plot(self.energyCalculator.time,self.energyCalculator.currentMinus)
        
        print(self.energyCalculator.result)

        ax1.annotate("Vmax",xy=self.energyCalculator.result["V max (V)"])
        ax1.annotate("Vhigh",xy=self.energyCalculator.result["V high (V)"])
        ax1.annotate("dv/dt",xy=self.energyCalculator.result["Rise / Falltime"])

        

        fig.tight_layout()
        self.energyGraphTab.GraphWidget.canvas.draw()


window = scopeCommander()
window.show()

app.exec()