from pathlib import Path

from nbs.core.audio import AudioEngine
from nbs.core.context import appctxt
from nbs.core.data import default_instruments
from nbs.ui.actions import (
    Actions,
    ChangeInstrumentActionsManager,
    SetCurrentInstrumentActionsManager,
)
from nbs.ui.menus import MenuBar
from nbs.ui.toolbar import InstrumentToolBar, ToolBar
from nbs.ui.workspace import *
from nbs.ui.workspace.layers import LayerArea
from nbs.ui.workspace.note_blocks import NoteBlockArea
from nbs.ui.workspace.piano import HorizontalAutoScrollArea, PianoWidget
from nbs.ui.workspace.time_bar import TimeBar
from nbs.ui.workspace.workspace import Workspace
from PyQt5 import QtCore, QtWidgets


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Minecraft Note Block Studio")
        self.setMinimumSize(854, 480)
        self.initAudio()
        self.initUI()
        self.initNoteBlocks()
        self.initPiano()
        self.initInstruments()

    def initAudio(self):
        self.audioEngine = AudioEngine(self)

    def initUI(self):
        self.menuBar = MenuBar()
        self.toolBar = ToolBar()
        self.instrumentBar = InstrumentToolBar()

        self.setMenuBar(self.menuBar)
        self.addToolBar(self.toolBar)
        self.addToolBar(self.instrumentBar)

        self.noteBlockArea = NoteBlockArea()
        self.layerArea = LayerArea()
        self.timeBar = TimeBar()
        self.piano = PianoWidget(keyCount=88, offset=9, validRange=(33, 57))
        self.pianoContainer = HorizontalAutoScrollArea()

        self.workspace = Workspace(self.noteBlockArea, self.layerArea, self.timeBar)
        self.centralArea = CentralArea(self.workspace, self.piano, self.pianoContainer)

        self.setCurrentInstrumentActionsManager = SetCurrentInstrumentActionsManager()
        self.changeInstrumentActionsManager = ChangeInstrumentActionsManager()

        self.setCentralWidget(self.centralArea)

    def initNoteBlocks(self):
        # Selection
        self.noteBlockArea.blockCountChanged.connect(Actions.setBlockCount)
        self.noteBlockArea.selectionChanged.connect(Actions.setSelectionStatus)
        self.noteBlockArea.selectionChanged.connect(lambda: Actions.setClipboard(True))

        Actions.cutAction.triggered.connect(self.noteBlockArea.cutSelection)
        Actions.copyAction.triggered.connect(self.noteBlockArea.copySelection)
        Actions.pasteAction.triggered.connect(self.noteBlockArea.pasteSelection)

        # Playback
        Actions.playPauseAction.triggered.connect(
            lambda checked: self.noteBlockArea.view.playbackManager.setPlaying(checked)
        )
        Actions.stopAction.triggered.connect(
            self.noteBlockArea.view.playbackManager.stop
        )

        # Sounds
        self.noteBlockArea.blockAdded.connect(
            lambda ins, key: self.audioEngine.playSound(
                ins, 0.5, 2 ** ((key - 45) / 12), 0
            )
        )
        self.noteBlockArea.blockPlayed.connect(
            lambda ins, key: self.audioEngine.playSound(
                ins, 0.5, 2 ** ((key - 45) / 12), 0
            )
        )

    def initPiano(self):
        # Set active workspace key
        self.piano.activeKeyChanged.connect(self.noteBlockArea.setActiveKey)

        # Sounds
        self.piano.activeKeyChanged.connect(
            lambda key: self.audioEngine.playSound(
                self.setCurrentInstrumentActionsManager.currentInstrument,
                0.5,
                2 ** ((key - 45) / 12),
                0,
            )
        )

    def initInstruments(self):
        for ins in default_instruments:
            sound_path = appctxt.get_resource(Path("sounds", ins.sound_path))
            self.audioEngine.loadSound(sound_path)

        # Set current instrument actions
        self.setCurrentInstrumentActionsManager.updateActions(default_instruments)
        self.setCurrentInstrumentActionsManager.instrumentChanged.connect(
            # TODO: connect this to future InstrumentManager object that will notify widgets
            self.noteBlockArea.setCurrentInstrument
            # self.centralWidget().workspace.piano.setValidRange(ins)
        )

        self.instrumentBar.populateInstruments()
        self.instrumentBar.instrumentButtonPressed.connect(
            lambda id_: self.audioEngine.playSound(id_, 0.5, 2 ** ((self.piano.activeKey - 45) / 12), 0)
        )

        # 'Change instrument...' actions
        self.changeInstrumentActionsManager.updateActions(default_instruments)
        self.changeInstrumentActionsManager

    #
    #
    #
    #
    #

    @QtCore.pyqtSlot()
    def new_song(self):
        # self.currentSong = nbs.core.data.Song()
        # TODO: save confirmation if editing unsaved work
        self.centralWidget().workspace.resetWorkspace()

    @QtCore.pyqtSlot()
    def load_song(self, filename=None):
        """Loads a .nbs file into the current session. passing a filename overrides opening the file dialog.
        loadFlag determines if the method is allowed to load the file and reset the workspace (needed in case the
        user presses cancel on the open file dialog)."""
        loadFlag = False

        if filename:
            loadFlag = True
        else:
            dialog = QtWidgets.QFileDialog(self)
            dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
            dialog.setWindowTitle("Open song")
            dialog.setLabelText(QtWidgets.QFileDialog.FileName, "Song name:")
            dialog.setNameFilter("Note Block Songs (*.nbs)")
            # dialog.restoreState()
            if dialog.exec():
                filename = dialog.selectedFiles()[0]
                # dialog.saveState()
                loadFlag = True

        # if loadFlag:
        #    self.currentSong = nbs.core.data.Song(filename=filename)
        #    self.centralWidget().workspace.resetWorkspace()
        #    # TODO: load layers
        #    for note in self.currentSong.notes:
        #        self.centralWidget().workspace.noteBlockWidget.addBlock(
        #            note.tick, note.layer, note.key, note.instrument
        #        )
        #    # It's really weird to updateSceneSize() here, there has to be a better solution.
        #    self.centralWidget().workspace.noteBlockWidget.updateSceneSize()

        # TODO: The main window should only interact with the workspace (consisting of layer area + note block area),
        # not directly with the note block area. The workspace will do the talking between the layer and note block
        # areas, keeping them in sync, and also provide an interface for interacting with both at the same time.

    @QtCore.pyqtSlot()
    def save_song(self):
        """Save current file without bringing up the save dialog if it has a defined location on disk"""
        if not self.currentSong.location:
            self.song_save_as()
        else:
            self.currentSong.save()

    @QtCore.pyqtSlot()
    def song_save_as(self):
        dialog = QtWidgets.QFileDialog(self)
        dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
        dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        dialog.setWindowTitle("Save song")
        dialog.setLabelText(QtWidgets.QFileDialog.FileName, "Song name:")
        dialog.setNameFilter("Note Block Songs (*.nbs)")
        # dialog.restoreState()
        if dialog.exec():
            location = dialog.selectedFiles()[0]
            self.currentSong.save(location)
            # dialog.saveState()
