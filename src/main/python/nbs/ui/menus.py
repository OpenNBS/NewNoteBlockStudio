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


class EditMenu(QtWidgets.QMenu):
    def __init__(self, parent=None, isFloat: bool = False):
        super().__init__(parent)
        self.isFloat = isFloat
        self.setTitle("Edit")
        self.addEntries()

    def addEntries(self):
        if self.isFloat:
            self.cutAction = self.addAction(Actions.cutAction)
            self.copyAction = self.addAction(Actions.copyAction)
            self.pasteAction = self.addAction(Actions.pasteAction)
            self.deleteAction = self.addAction(Actions.deleteAction)
        else:
            self.undoAction = self.addAction(Actions.undoAction)
            self.redoAction = self.addAction(Actions.redoAction)
        self.addSeparator()

        self.copyAction = self.addAction(Actions.copyAction)
        self.cutAction = self.addAction(Actions.cutAction)
        self.pasteAction = self.addAction(Actions.pasteAction)
        self.deleteAction = self.addAction(Actions.deleteAction)
        self.addSeparator()

        self.selectAllAction = self.addAction(Actions.selectAllAction)
        self.deselectAllAction = self.addAction(Actions.deselectAllAction)
        self.invertSelectionAction = self.addAction(Actions.invertSelectionAction)
        self.addSeparator()

        if self.isFloat:
            self.selectAllLeftAction = self.addAction(Actions.selectAllLeftAction)
            self.selectAllRightAction = self.addAction(Actions.selectAllRightAction)
            self.addSeparator()

        self.selectAllInstrumentAction = self.addAction(
            Actions.selectAllInstrumentAction
        )
        self.selectAllButInstrumentAction = self.addAction(
            Actions.selectAllButInstrumentAction
        )
        self.addSeparator()

        self.increaseOctaveAction = self.addAction(Actions.increaseOctaveAction)
        self.decreaseOctaveAction = self.addAction(Actions.decreaseOctaveAction)
        self.increaseKeyAction = self.addAction(Actions.increaseKeyAction)
        self.decreaseKeyAction = self.addAction(Actions.decreaseKeyAction)
        self.changeInstrumentMenu = self.addMenu("Change instrument...")
        self.addSeparator()

        self.expandSelectionAction = self.addAction(Actions.expandSelectionAction)
        self.compressSelectionAction = self.addAction(Actions.compressSelectionAction)
        self.addSeparator()

        self.transposeNotesAction = self.addAction(Actions.transposeNotesAction)
        self.macrosMenu = self.addMenu("Macros...")

    def lockSelectionEntries(self, lock: bool):
        pass

    def addInstrumentEntry(self, instrument):
        pass

    def removeInstrumentEntry(self, index):
        pass


class SettingsMenu(QtWidgets.QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Settings")
        self.addEntries()

    def addEntries(self):
        self.instrumentsMenu = self.addMenu("Instrument")
        self.instrumentsMenu.addAction("Harp")
        self.instrumentSettingsAction = self.addAction(Actions.instrumentSettingsAction)
        self.addSeparator()

        self.songInfoAction = self.addAction(Actions.songInfoAction)
        self.songPropertiesAction = self.addAction(Actions.songPropertiesAction)
        self.songStatsAction = self.addAction(Actions.songStatsAction)
        self.addSeparator()

        self.deviceManagerAction = self.addAction(Actions.deviceManagerAction)
        self.preferencesAction = self.addAction(Actions.preferencesAction)


class HelpMenu(QtWidgets.QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Help")
        self.addEntries()

    def addEntries(self):
        self.websiteAction = self.addAction(Actions.websiteAction)
        self.githubAction = self.addAction(Actions.githubAction)
        self.discordAction = self.addAction(Actions.discordAction)
        self.reportBugAction = self.addAction(Actions.reportBugAction)
        self.donateAction = self.addAction(Actions.donateAction)
        self.addSeparator()

        self.changelogAction = self.addAction(Actions.changelogAction)
        self.aboutAction = self.addAction(Actions.aboutAction)


class MenuBar(QtWidgets.QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.fileMenu = FileMenu()
        self.editMenu = EditMenu(isFloat=False)
        self.settingsMenu = SettingsMenu()
        self.helpMenu = HelpMenu()

        self.addMenu(self.fileMenu)
        self.addMenu(self.editMenu)
        self.addMenu(self.settingsMenu)
        self.addMenu(self.helpMenu)
