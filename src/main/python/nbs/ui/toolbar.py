from nbs.ui.actions import Actions
from PyQt5 import QtWidgets


class ToolBar(QtWidgets.QToolBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.addActions()

    def addActions(self):
        self.newSongAction = self.addAction(Actions.newSongAction)
        self.openSongAction = self.addAction(Actions.openSongAction)
        self.saveSongAction = self.addAction(Actions.saveSongAction)
        self.addSeparator()

        self.playPauseAction = self.addAction(Actions.playPauseAction)
        self.stopAction = self.addAction(Actions.stopAction)
        self.rewindAction = self.addAction(Actions.rewindAction)
        self.fastForwardAction = self.addAction(Actions.fastForwardAction)
        self.recordAction = self.addAction(Actions.rewindAction)
        self.loopAction = self.addAction(Actions.loopAction)
        self.addSeparator()

        self.undoAction = self.addAction(Actions.undoAction)
        self.redoAction = self.addAction(Actions.redoAction)
        self.cutAction = self.addAction(Actions.cutAction)
        self.copyAction = self.addAction(Actions.copyAction)
        self.pasteAction = self.addAction(Actions.pasteAction)
        self.deleteAction = self.addAction(Actions.deleteAction)
        self.addSeparator()

        self.songInfoAction = self.addAction(Actions.songInfoAction)
        self.songPropertiesAction = self.addAction(Actions.songPropertiesAction)
        self.instrumentSettingsAction = self.addAction(Actions.instrumentSettingsAction)
        self.deviceManagerAction = self.addAction(Actions.deviceManagerAction)
        self.preferencesAction = self.addAction(Actions.preferencesAction)
        self.addSeparator()

        self.websiteAction = self.addAction(Actions.websiteAction)

        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        self.addWidget(spacer)

        self.addAction("Compatible")

    def lockSelectionEntries(self, lock: bool):
        pass

    def addInstrumentEntry(self, instrument):
        pass

    def removeInstrumentEntry(self, index):
        pass
