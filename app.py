import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
import interface

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Open Note Block Studio')
        self.setMinimumSize(854, 480)
        #self.setGeometry(100, 100, 280, 80)
        #self.move(60, 15)
        #self.setFocus()

        menuBar = interface.drawMenuBar(self)
        toolBar = interface.drawToolBar(self)
        mainArea = interface.drawMainArea(self)

        # replace all this with a single class/function that draws all
        #mainArea = interface.MainArea()


        self.setMenuBar(menuBar)
        self.addToolBar(toolBar)
        self.setCentralWidget(mainArea)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())