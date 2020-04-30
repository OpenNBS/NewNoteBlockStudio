from PyQt5 import QtWidgets
import nbs.ui.components
import nbs.core.data

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

        current_song = nbs.core.data.Song(song_dict={"header": None, "layers": None, "instruments": None,
                                                     "notes": [{"tick": 0, "layer": 1, "key": 1, "instrument": 0},
                                                               {"tick": 1, "layer": 2, "key": 2, "instrument": 0},
                                                               {"tick": 2, "layer": 3, "key": 3, "instrument": 0},
                                                               {"tick": 3, "layer": 4, "key": 4, "instrument": 0},
                                                               {"tick": 4, "layer": 5, "key": 5, "instrument": 0}]})  # testing
        for note in current_song.notes:
            mainArea.workspace.noteBlockWidget.addBlock(note["tick"], note["layer"], note["key"], note["instrument"])

    def drawMenuBar(self):
        pass

    def drawToolBar(self):
        pass

    def drawStatusBar(self):
        pass
