from PyQt5 import QtWidgets
import nbs.ui.components

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Minecraft Note Block Studio")
        self.setMinimumSize(854, 480)

        menuBar = nbs.ui.components.drawMenuBar(self)
        toolBar = nbs.ui.components.drawToolBar(self)
        mainArea = nbs.ui.components.CentralArea(self)

        self.setMenuBar(menuBar)
        self.addToolBar(toolBar)
        self.setCentralWidget(mainArea)

        nb = nbs.ui.components.NoteBlock(0, 5, 33, 0)
        mainArea.workspace.noteBlockWidget.addItem(nb)

    def drawMenuBar(self):
        pass

    def drawToolBar(self):
        pass

    def drawStatusBar(self):
        pass
