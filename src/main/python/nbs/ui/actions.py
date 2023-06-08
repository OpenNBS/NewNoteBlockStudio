from typing import Sequence

import qtawesome as qta
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QActionGroup

from nbs.controller.instrument import InstrumentInstance
from nbs.core.context import appctxt
from nbs.core.data import Instrument


class Actions(QtCore.QObject):
    @classmethod
    def initActions(cls):

        # qta.icon can't be on the top level of the module, so we must
        # put everything into a method and call it after QApplication
        # is created. See https://github.com/spyder-ide/qtawesome/issues/144

        # TODO: There's probably a better way to do this...

        icons = {
            # fmt: off
            "new_song":         qta.icon('mdi.file-plus'),
            "open_song":        qta.icon('mdi.folder-open'),
            "save_song":        qta.icon('mdi.content-save'),
            "save_song_as":     qta.icon('mdi.content-save-all'),
            "rewind":           qta.icon('mdi.rewind'),
            "fast_forward":     qta.icon('mdi.fast-forward'),
            "play_pause":       qta.icon('mdi.play', selected='mdi.pause'),
            "stop":             qta.icon('mdi.stop'),
            "record":           qta.icon('mdi.record'),
            "loop":             qta.icon('mdi.repeat'),
            "loop_off":         qta.icon('mdi.repeat-off'),
            "undo":             qta.icon('mdi.undo'),
            "redo":             qta.icon('mdi.redo'),
            "cut":              qta.icon('mdi.content-cut'),
            "copy":             qta.icon('mdi.content-copy'),
            "paste":            qta.icon('mdi.content-paste'),
            "delete":           qta.icon('mdi.delete'),
            "select_all":       qta.icon('mdi.select-all'),
            "song_instruments": qta.icon('mdi.piano'),
            "song_info":        qta.icon('mdi.information'),
            "song_properties":  qta.icon('mdi.label'),
            "song_stats":       qta.icon('mdi.file-document-edit'),
            "midi_devices":     qta.icon('mdi.usb'),
            "settings":         qta.icon('mdi.cog'),
            "website":          qta.icon('mdi.web'),
            "github":           qta.icon('mdi.github'),
            "discord":          qta.icon('mdi.discord'),
            "report_bug":       qta.icon('mdi.bug'),
            "donate":           qta.icon('mdi.heart'),
            "changelog":        qta.icon('mdi.text-box'),
            "about":            qta.icon('mdi.information'),
            "":                 QIcon()
            # fmt: on
        }

        # File
        cls.newSongAction = QAction(icons["new_song"], "New song")
        cls.openSongAction = QAction(icons["open_song"], "Open song...")
        cls.saveSongAction = QAction(icons["save_song"], "Save song")
        cls.saveSongAsAction = QAction(
            icons["save_song_as"], "Save song as a new file..."
        )
        cls.saveOptionsAction = QAction("Save options...")
        cls.importPatternAction = QAction("Import pattern...")
        cls.exportPatternAction = QAction("Export pattern...")
        cls.importMidiAction = QAction("Import MIDI...")
        cls.exportMidiAction = QAction("Export MIDI...")
        cls.exportSchematicAction = QAction("Export schematic...")
        cls.exportAudioAction = QAction("Export as audio file...")
        cls.exportDatapackAction = QAction("Export as data pack...")
        cls.exitAction = QAction("Exit")

        # Playback
        cls.playPauseAction = QAction(icons["play_pause"], "Play/Pause song")
        cls.playPauseAction.setCheckable(True)
        cls.stopAction = QAction(icons["stop"], "Stop song")
        cls.fastForwardAction = QAction(icons["fast_forward"], "Fast-forward song")
        cls.rewindAction = QAction(icons["rewind"], "Rewind song")
        cls.loopAction = QAction(icons["loop"], "Toggle looping")
        cls.loopAction.setCheckable(True)
        cls.metronomeAction = QAction(icons[""], "Toggle metronome")
        cls.metronomeAction.setCheckable(True)

        # Edit
        cls.undoAction = QAction(icons["undo"], "Undo")
        cls.redoAction = QAction(icons["redo"], "Redo")
        cls.copyAction = QAction(icons["copy"], "Copy")
        cls.cutAction = QAction(icons["cut"], "Cut")
        cls.pasteAction = QAction(icons["paste"], "Paste")
        cls.deleteAction = QAction(icons["delete"], "Delete")
        cls.selectAllAction = QAction(icons["select_all"], "Select all")
        cls.deselectAllAction = QAction(icons[""], "Deselect all")
        cls.invertSelectionAction = QAction(icons[""], "Invert selection")
        cls.selectAllLeftAction = QAction(icons[""], "Select all to the left <-")
        cls.selectAllRightAction = QAction(icons[""], "Select all to the right ->")
        cls.selectAllInstrumentAction = QAction(icons[""], "Select all {}")
        cls.selectAllButInstrumentAction = QAction(icons[""], "Select all but {}")
        cls.increaseOctaveAction = QAction(icons[""], "Increase octave")
        cls.decreaseOctaveAction = QAction(icons[""], "Decrease octave")
        cls.increaseKeyAction = QAction(icons[""], "Increase key")
        cls.decreaseKeyAction = QAction(icons[""], "Decrease key")
        cls.expandSelectionAction = QAction(icons[""], "Expand selection")
        cls.compressSelectionAction = QAction(icons[""], "Compress selection")
        cls.transposeNotesAction = QAction(
            icons[""], "Transpose notes outside octave range"
        )

        # Edit modes
        cls.setEditMode = QActionGroup(None)
        cls.setEditModeKeyAction = QAction(
            icons[""], "Edit note key", parent=cls.setEditMode
        )
        cls.setEditModeVelocityAction = QAction(
            icons[""], "Edit note velocity", parent=cls.setEditMode
        )
        cls.setEditModePanningAction = QAction(
            icons[""], "Edit note panning", parent=cls.setEditMode
        )
        cls.setEditModePitchAction = QAction(
            icons[""], "Edit note pitch", parent=cls.setEditMode
        )

        # Settings
        cls.instrumentSettingsAction = QAction(
            icons["song_instruments"], "Instrument settings..."
        )
        cls.songInfoAction = QAction(icons["song_info"], "Song info...")
        cls.songPropertiesAction = QAction(
            icons["song_properties"], "Song properties..."
        )
        cls.songStatsAction = QAction(icons["song_stats"], "Song stats...")
        cls.deviceManagerAction = QAction(
            icons["midi_devices"], "MIDI device manager..."
        )
        cls.preferencesAction = QAction(icons["settings"], "Preferences...")
        cls.compatibilityAction = QAction(
            icons[""], "Compatible"
        )

        # About
        cls.websiteAction = QAction(icons["website"], "Website...")
        cls.githubAction = QAction(icons["github"], "GitHub...")
        cls.discordAction = QAction(icons["discord"], "Discord server...")
        cls.reportBugAction = QAction(icons["report_bug"], "Report a bug...")
        cls.donateAction = QAction(icons["donate"], "Donate...")
        cls.changelogAction = QAction(icons["changelog"], "Changelog...")
        cls.aboutAction = QAction(icons["about"], "About...")

        cls.setClipboard(False)
        cls.setBlockCount(0)
        cls.setSelectionStatus(-2)

    @classmethod
    def setClipboard(cls, hasClipboard: bool) -> None:
        """Set actions that should only be enabled when there is something in the clipboard."""
        cls.pasteAction.setEnabled(hasClipboard)

    @classmethod
    def setEmptyActionsEnabled(cls, enabled: bool = True):
        """Set actions that should only be enabled when at least one note block exists."""
        cls.saveSongAction.setEnabled(enabled)
        cls.saveSongAsAction.setEnabled(enabled)
        cls.saveOptionsAction.setEnabled(enabled)
        cls.exportPatternAction.setEnabled(enabled)
        cls.exportMidiAction.setEnabled(enabled)
        cls.exportSchematicAction.setEnabled(enabled)
        cls.exportAudioAction.setEnabled(enabled)
        cls.exportDatapackAction.setEnabled(enabled)
        cls.invertSelectionAction.setEnabled(enabled)

    @classmethod
    def setSelectionActionsEnabled(cls, enabled: bool = True):
        """Set actions that should only be enabled when there is a selection."""
        cls.cutAction.setEnabled(enabled)
        cls.copyAction.setEnabled(enabled)
        cls.deleteAction.setEnabled(enabled)
        cls.deselectAllAction.setEnabled(enabled)
        cls.increaseOctaveAction.setEnabled(enabled)
        cls.decreaseOctaveAction.setEnabled(enabled)
        cls.increaseKeyAction.setEnabled(enabled)
        cls.decreaseKeyAction.setEnabled(enabled)
        # cls.changeInstrumentActionGroup.setEnabled(enabled)
        cls.expandSelectionAction.setEnabled(enabled)
        cls.compressSelectionAction.setEnabled(enabled)
        cls.transposeNotesAction.setEnabled(enabled)
        # cls.macrosActionGroup.setEnabled(enabled)

    @classmethod
    def setFullSelectionActionsEnabled(cls, enabled: bool = False):
        """Set actions that should be disabled when all note blocks are selected."""
        cls.selectAllAction.setEnabled(enabled)
        cls.selectAllLeftAction.setEnabled(enabled)
        cls.selectAllRightAction.setEnabled(enabled)
        cls.selectAllInstrumentAction.setEnabled(enabled)
        cls.selectAllButInstrumentAction.setEnabled(enabled)

    @QtCore.pyqtSlot(int)
    def setSelectionStatus(selection: int) -> None:
        """Enable or disable the necessary actions according to the given selection status."""
        if selection == -1:
            Actions.setNoneSelected()
        elif selection == 0:
            Actions.setSomeSelected()
        elif selection == 1:
            Actions.setAllSelected()

    @QtCore.pyqtSlot(int)
    def setBlockCount(blockCount: int) -> None:
        if blockCount == 0:
            Actions.setEmpty()
        else:
            Actions.setEmptyActionsEnabled(True)

    @classmethod
    def setEmpty(cls):
        """Call this when no note blocks exist."""
        cls.setEmptyActionsEnabled(False)
        cls.setSelectionActionsEnabled(False)
        cls.setFullSelectionActionsEnabled(False)
        cls.invertSelectionAction.setEnabled(False)

    @classmethod
    def setAllSelected(cls):
        """Call this when all note blocks are selected."""
        cls.setSelectionActionsEnabled(True)
        cls.setFullSelectionActionsEnabled(False)

    @classmethod
    def setSomeSelected(cls):
        """Call this when some note blocks are selected."""
        cls.setSelectionActionsEnabled(True)
        cls.setFullSelectionActionsEnabled(True)

    @classmethod
    def setNoneSelected(cls):
        """Call this when no note blocks are selected."""
        cls.setSelectionActionsEnabled(False)
        cls.setFullSelectionActionsEnabled(True)


setCurrentInstrumentActions = []
changeInstrumentActions = []


class SetCurrentInstrumentActionsManager(QtCore.QObject):
    """Handle actions responsible for changing the currently active instrument."""

    instrumentChanged = QtCore.pyqtSignal(int)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.actionGroup = QActionGroup(self)
        self.actionGroup.setExclusive(True)
        self.actionGroup.triggered.connect(
            lambda action: self.instrumentChanged.emit(action.data())
        )

    @QtCore.pyqtSlot(list)
    def updateActions(self, instruments: Sequence[InstrumentInstance]):
        """Update the list of instruments."""
        global setCurrentInstrumentActions
        setCurrentInstrumentActions = []

        for id_, instrument in enumerate(instruments):
            action = QAction(f"{instrument.name}")
            action.setData(id_)
            action.setCheckable(True)

            action.setIcon(instrument.icon)
            action.setIconText(f"Change instrument to {instrument.name}")
            action.setIconVisibleInMenu(False)

            self.actionGroup.addAction(action)
            setCurrentInstrumentActions.append(action)

    @property
    def currentInstrument(self):
        return self.actionGroup.checkedAction().data()

    @currentInstrument.setter
    def currentInstrument(self, id_: int):
        global setCurrentInstrumentActions
        if id_ < 0 or id_ >= len(setCurrentInstrumentActions):
            raise ValueError(f"Invalid instrument ID: {id}")
        setCurrentInstrumentActions[id_].setChecked(True)
        self.instrumentChanged.emit(id_)


class ChangeInstrumentActionsManager(QtCore.QObject):
    """Handle actions responsible for changing the instrument of a selection."""

    instrumentChanged = QtCore.pyqtSignal(int)

    # TODO: Perhaps here we should have individual add/remove/swapInstrument slots,
    # because populating an entire menu when it's about to show is acceptable, but creating new
    # QActions every time an instrument is changed might be too expensive.
    # Or, instead, updateInstruments could be smart about which actions to keep or remove by detecting
    # what changed in the list of instruments.

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.actionGroup = QActionGroup(self)
        self.actionGroup.triggered.connect(
            lambda action: self.instrumentChanged.emit(action.data())
        )

    @QtCore.pyqtSlot(list)
    def updateActions(self, instruments: Sequence[Instrument]):
        """Update the list of instruments."""
        global changeInstrumentActions
        changeInstrumentActions = []
        for id_, instrument in enumerate(instruments):
            action = QAction(f"...to {instrument.name}")
            action.setData(id_)
            self.actionGroup.addAction(action)
            changeInstrumentActions.append(action)
