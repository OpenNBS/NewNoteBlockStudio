from typing import Sequence

import nbs.ui.actions as actions
from nbs.core.data import Instrument
from nbs.ui.actions import Actions
from nbs.ui.workspace.constants import appctxt
from PyQt5 import QtCore, QtGui, QtWidgets


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


class InstrumentButton(QtWidgets.QToolButton):
    def __init__(self, instrument: Instrument, action: QtWidgets.QAction, parent=None):
        super().__init__(parent)
        self.setDefaultAction(action)

        icon = QtGui.QIcon(
            appctxt.get_resource(f"images/instruments/{instrument.icon_path}")
        )
        self.setIcon(icon)
        self.setToolTip(f"Change instrument to {instrument.name}")


class InstrumentToolBar(QtWidgets.QToolBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        # self.populateInstruments(instruments)

    @QtCore.pyqtSlot(object)
    def populateInstruments(self, instruments: Sequence[Instrument]):
        self.clear()
        for instrument, action in zip(instruments, actions.setCurrentInstrumentActions):
            print(instrument.name)
            button = InstrumentButton(instrument, action, parent=self)
            self.addWidget(button)
