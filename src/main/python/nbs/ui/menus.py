from PyQt5 import QtGui, QtWidgets
from nbs.ui.actions import Actions


class FileMenu(QtWidgets.QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)
        Actions.initActions()
        self.setTitle("File")
        self.addEntries()

    def addEntries(self):
        self.newSongAction = self.addAction(Actions.newSongAction)
        self.openSongAction = self.addAction(Actions.openSongAction)

        # Recent songs
        self.recentSongs = self.addMenu(QtGui.QIcon(), "Open recent")
        self.recentSongs.addSection(QtGui.QIcon(), "No recent songs")

        # Import
        self.importMenu = self.addMenu("Import")
        self.importFromMidiAction = self.importMenu.addAction(Actions.importMidiAction)

        self.addSeparator()

        self.saveSongAction = self.addAction(Actions.saveSongAction)
        self.saveSongAsAction = self.addAction(Actions.saveSongAsAction)

        # Export
        self.exportMenu = self.addMenu("Export as...")
        self.exportMenu.addAction(Actions.exportMidiAction)
        self.exportMenu.addAction(Actions.exportAudioAction)
        self.exportMenu.addAction(Actions.exportSchematicAction)
        self.exportMenu.addAction(Actions.exportDatapackAction)

        self.addSeparator()

        self.exitAction = self.addAction(Actions.exitAction)

    def updateRecentSongs(self):
        pass
