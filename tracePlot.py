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

class screenCaptureWidget(QtWidgets.QLabel):
    def __init__(self, parent=None):
        QtWidgets.QLabel.__init__(self, parent)   # Inherit from QWidget
        pixmap = QPixmap("./DS1Z_QuickPrint7.png")
        self.setPixmap(pixmap)
        self.setText("asd")
        print("pppppppp")

#class screenCaptureCanvas(Canvas):
#    def __init__(self):
#        self.fig = Figure()
#        self.ax = self.fig.add_subplot(111)
#        self.fig.tight_layout()
#
#        Canvas.__init__(self, self.fig)
#        Canvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
#        Canvas.updateGeometry(self)