from PyQt5 import QtWidgets
from window import Window
import sys

qapp = QtWidgets.QApplication([])
application = Window()
application.show()
sys.exit(qapp.exec())