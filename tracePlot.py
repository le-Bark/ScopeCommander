from PyQt5 import QtWidgets
from PyQt5.QtGui import QPixmap
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
import matplotlib

matplotlib.use('QT5Agg')

class tracePlotterCanvas(Canvas):
    def __init__(self):
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.fig.tight_layout()
        self.ax.set_xmargin(0)
        self.ax.set_ymargin(0)
        Canvas.__init__(self, self.fig)
        Canvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        Canvas.updateGeometry(self)

class tracePlotterWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)   # Inherit from QWidget
        self.canvas = tracePlotterCanvas()         # Create canvas object
        self.vbl = QtWidgets.QVBoxLayout()         # Set box for plotting
        self.vbl.addWidget(self.canvas)
        self.vbl.addWidget(NavigationToolbar(self.canvas,self))
        self.setLayout(self.vbl)

class graphTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setEnabled(True)
        self.setObjectName("GraphTab")

        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        #self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.GraphWidget = tracePlotterWidget(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.GraphWidget.sizePolicy().hasHeightForWidth())
        self.GraphWidget.setSizePolicy(sizePolicy)
        self.GraphWidget.setObjectName("GraphWidget")
        self.verticalLayout.addWidget(self.GraphWidget)


