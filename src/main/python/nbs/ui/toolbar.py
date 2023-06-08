from PyQt5 import QtCore, QtWidgets

import nbs.ui.actions as actions
from nbs.ui.actions import Actions


class PlaybackToolBar(QtWidgets.QToolBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(False)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred
        )
        self.addActions()

    def addActions(self):
        self.newAction = self.addAction(Actions.newSongAction)
        self.openAction = self.addAction(Actions.openSongAction)
        self.saveAction = self.addAction(Actions.saveSongAction)
        self.saveAsAction = self.addAction(Actions.saveSongAsAction)
        self.addSeparator()
        self.playPauseAction = self.addAction(Actions.playPauseAction)
        self.stopAction = self.addAction(Actions.stopAction)
        self.rewindAction = self.addAction(Actions.rewindAction)
        self.fastForwardAction = self.addAction(Actions.fastForwardAction)
        self.recordAction = self.addAction(Actions.rewindAction)
        self.loopAction = self.addAction(Actions.loopAction)
        self.metronomeAction = self.addAction(Actions.metronomeAction)


class EditToolBar(QtWidgets.QToolBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(False)
        self.setMinimumWidth(450)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred
        )
        self.addActions()

    def addActions(self):
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

        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        self.addWidget(spacer)

        self.compatibilityAction = self.addAction("Compatible")


class InstrumentToolBar(QtWidgets.QToolBar):
    instrumentButtonPressed = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.buttonGroup = QtWidgets.QButtonGroup(self)
        self.setMovable(True)
        self.setFloatable(False)
        self.buttonGroup.idClicked.connect(self.instrumentButtonPressed)

    @QtCore.pyqtSlot(list)
    def populateInstruments(self):
        self.clear()
        for id_, action in enumerate(actions.setCurrentInstrumentActions):
            button = QtWidgets.QToolButton(parent=self)
            button.setDefaultAction(action)

            self.addWidget(button)
            self.buttonGroup.addButton(button)
            self.buttonGroup.setId(button, id_)
