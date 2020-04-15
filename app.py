import sys
import os
from PyQt5 import QtCore, QtWidgets
import interface

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Open Note Block Studio')
        self.setMinimumSize(854, 480)
        #self.setGeometry(100, 100, 280, 80)
        #self.move(60, 15)
        #self.setFocus()

        menuBar = interface.drawMenuBar(self)
        toolBar = interface.drawToolBar(self)
        mainArea = interface.CentralArea(self)

        # replace all this with a single class/function that draws all
        #mainArea = interface.MainArea()


        self.setMenuBar(menuBar)
        self.addToolBar(toolBar)
        self.setCentralWidget(mainArea)

if __name__ == '__main__':
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    app = QtWidgets.QApplication(sys.argv)
    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())