from typing import List, Optional

from PyQt5 import QtCore, QtGui, QtWidgets

from nbs.core.data import Instrument
from nbs.ui.actions import Actions


class FileMenu(QtWidgets.QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)
        Actions.initActions()
        self.setTitle("File")
        self.addEntries()

    def addEntries(self):
        self.addAction(Actions.newSongAction)
        self.addAction(Actions.openSongAction)

        # Recent songs
        self.recentSongs = self.addMenu(QtGui.QIcon(), "Open recent")
        self.recentSongs.addSection(QtGui.QIcon(), "No recent songs")

        # Import
        self.importMenu = self.addMenu("Import")
        self.importMenu.addAction(Actions.importMidiAction)

        self.addSeparator()

        self.addAction(Actions.saveSongAction)
        self.addAction(Actions.saveSongAsAction)

        # Export
        self.exportMenu = self.addMenu("Export as...")
        self.exportMenu.addAction(Actions.exportMidiAction)
        self.exportMenu.addAction(Actions.exportAudioAction)
        self.exportMenu.addAction(Actions.exportSchematicAction)
        self.exportMenu.addAction(Actions.exportDatapackAction)

        self.addSeparator()

        self.addAction(Actions.exitAction)

    def updateRecentSongs(self):
        pass


class InstrumentEditSubMenu(QtWidgets.QMenu):
    instrumentChanged = QtCore.pyqtSignal(int)

    def __init__(
        self,
        actionList: List[QtWidgets.QAction],
        parent: Optional[QtWidgets.QWidget] = None,
    ):
        super().__init__(parent=parent)
        self.actionList = actionList
        self.setTitle("Change instrument...")
        self.aboutToShow.connect(self.populateActions)

    def populateActions(self) -> None:
        self.clear()
        for action in self.actionList:
            self.addAction(action)


class InstrumentSettingsSubMenu(QtWidgets.QMenu):
    instrumentChanged = QtCore.pyqtSignal(int)

    def __init__(
        self,
        actionList: List[QtWidgets.QAction],
        parent: Optional[QtWidgets.QWidget] = None,
    ):
        super().__init__(parent)
        self.actionList = actionList
        self.setTitle("Instrument")
        self.aboutToShow.connect(self.populateActions)

    def populateActions(self) -> None:
        self.clear()
        for action in self.actionList:
            self.addAction(action)


class EditMenu(QtWidgets.QMenu):
    def __init__(
        self,
        instrumentActions: List[QtWidgets.QAction] = [],
        parent: Optional[QtWidgets.QWidget] = None,
        isContextMenu: bool = False,
    ):
        super().__init__(parent)
        self.instrumentActions = instrumentActions
        self.isContextMenu = isContextMenu
        self.setTitle("Edit")
        self.addEntries()

    def addEntries(self):
        if self.isContextMenu:
            self.addAction(Actions.cutAction)
            self.addAction(Actions.copyAction)
            self.addAction(Actions.pasteAction)
            self.addAction(Actions.deleteAction)
        else:
            self.addAction(Actions.undoAction)
            self.addAction(Actions.redoAction)
        self.addSeparator()

        self.addAction(Actions.copyAction)
        self.addAction(Actions.cutAction)
        self.addAction(Actions.pasteAction)
        self.addAction(Actions.deleteAction)
        self.addSeparator()

        self.addAction(Actions.selectAllAction)
        self.addAction(Actions.deselectAllAction)
        self.addAction(Actions.invertSelectionAction)
        self.addSeparator()

        if self.isContextMenu:
            self.addAction(Actions.selectAllLeftAction)
            self.addAction(Actions.selectAllRightAction)
            self.addSeparator()

        self.addAction(Actions.selectAllInstrumentAction)
        self.addAction(Actions.selectAllButInstrumentAction)
        self.addSeparator()

        self.addAction(Actions.increaseOctaveAction)
        self.addAction(Actions.decreaseOctaveAction)
        self.addAction(Actions.increaseKeyAction)
        self.addAction(Actions.decreaseKeyAction)
        self.changeInstrumentMenu = InstrumentEditSubMenu(
            actionList=self.instrumentActions, parent=self
        )
        self.addMenu(self.changeInstrumentMenu)
        self.addSeparator()

        self.addAction(Actions.expandSelectionAction)
        self.addAction(Actions.compressSelectionAction)
        self.addSeparator()

        self.addAction(Actions.transposeNotesAction)
        self.macrosMenu = self.addMenu("Macros...")

    @QtCore.pyqtSlot(str)
    def changeCurrentInstrument(self, instrument: Instrument):
        Actions.selectAllInstrumentAction.setText(f"Select all {instrument.name}")
        Actions.selectAllButInstrumentAction.setText(
            f"Select all but {instrument.name}"
        )


class SettingsMenu(QtWidgets.QMenu):
    def __init__(
        self,
        instrumentActions: List[QtWidgets.QAction],
        parent: Optional[QtWidgets.QWidget] = None,
    ):
        super().__init__(parent)
        self.instrumentActions = instrumentActions
        self.setTitle("Settings")
        self.addEntries()

    def addEntries(self):
        self.instrumentMenu = InstrumentSettingsSubMenu(
            actionList=self.instrumentActions, parent=self
        )
        self.addMenu(self.instrumentMenu)
        self.addAction(Actions.instrumentSettingsAction)
        self.addSeparator()

        self.addAction(Actions.songInfoAction)
        self.addAction(Actions.songPropertiesAction)
        self.addAction(Actions.songStatsAction)
        self.addSeparator()

        self.addAction(Actions.deviceManagerAction)
        self.addAction(Actions.preferencesAction)


class HelpMenu(QtWidgets.QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Help")
        self.addEntries()

    def addEntries(self):
        self.addAction(Actions.websiteAction)
        self.addAction(Actions.githubAction)
        self.addAction(Actions.discordAction)
        self.addAction(Actions.reportBugAction)
        self.addAction(Actions.donateAction)
        self.addSeparator()

        self.addAction(Actions.changelogAction)
        self.addAction(Actions.aboutAction)


class MenuBar(QtWidgets.QMenuBar):
    def __init__(
        self,
        setCurrentInstrumentActions: List[QtWidgets.QAction],
        changeInstrumentActions: List[QtWidgets.QAction],
        parent: Optional[QtWidgets.QWidget] = None,
    ):
        super().__init__(parent)
        self.setCurrentInstrumentActions = setCurrentInstrumentActions
        self.changeInstrumentActions = changeInstrumentActions
        self.initUI()

    def initUI(self):
        self.fileMenu = FileMenu()
        self.editMenu = EditMenu(
            instrumentActions=self.changeInstrumentActions, isContextMenu=False
        )
        self.settingsMenu = SettingsMenu(
            instrumentActions=self.setCurrentInstrumentActions
        )
        self.helpMenu = HelpMenu()

        self.addMenu(self.fileMenu)
        self.addMenu(self.editMenu)
        self.addMenu(self.settingsMenu)
        self.addMenu(self.helpMenu)
