from pathlib import Path

from nbs.controller.playback import PlaybackController
from nbs.core.audio import AudioEngine
from nbs.core.context import appctxt
from nbs.core.data import default_instruments
from nbs.core.song import Song
from nbs.ui.actions import (
    Actions,
    ChangeInstrumentActionsManager,
    SetCurrentInstrumentActionsManager,
)
from nbs.ui.file import getLoadSongDialog
from nbs.ui.menus import MenuBar
from nbs.ui.toolbar import ToolBar
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
        self.initTimeBar()
        self.initPiano()
        self.initInstruments()
        self.initFile()

    def initAudio(self):
        self.audioEngine = AudioEngine(self)

    def initUI(self):
        self.menuBar = MenuBar()
        self.toolBar = ToolBar()
        # self.instrumentBar = InstrumentToolBar()

        self.setMenuBar(self.menuBar)
        self.addToolBar(self.toolBar)
        # self.addToolBar(self.instrumentBar)

        self.playbackController = PlaybackController()

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
        Actions.playPauseAction.triggered.connect(self.playbackController.setPlaying)
        Actions.stopAction.triggered.connect(self.playbackController.stop)

        self.playbackController.playbackPositionChanged.connect(
            self.noteBlockArea.view.setPlaybackPosition
        )
        self.noteBlockArea.view.playbackPositionChanged.connect(
            self.playbackController.setPlaybackPosition
        )

        # Sounds
        self.noteBlockArea.blockAdded.connect(
            lambda ins, key: self.audioEngine.playSound(ins, 0.5, key - 45, 0)
        )
        self.noteBlockArea.tickPlayed.connect(
            lambda sounds: self.audioEngine.playSounds(
                ((ins, 0.5, key - 45, 0) for ins, key, *_ in sounds)
            )
        )

    def initTimeBar(self):
        self.timeBar.tempoChanged.connect(self.playbackController.setTempo)
        self.playbackController.playbackPositionChanged.connect(
            self.timeBar.currentTimeChanged
        )

    def initPiano(self):
        # Set active workspace key
        self.piano.activeKeyChanged.connect(self.noteBlockArea.setActiveKey)
        self.piano.activeKey = 39

        # Sounds
        self.piano.activeKeyChanged.connect(
            lambda key: self.audioEngine.playSound(
                self.setCurrentInstrumentActionsManager.currentInstrument,
                0.5,
                key - 45,
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
        self.setCurrentInstrumentActionsManager.currentInstrument = 0

        self.toolBar.populateInstruments()
        self.toolBar.instrumentButtonPressed.connect(
            lambda id_: self.audioEngine.playSound(
                id_, 0.5, self.piano.activeKey - 45, 0
            )
        )

        # 'Change instrument...' actions
        self.changeInstrumentActionsManager.updateActions(default_instruments)
        self.changeInstrumentActionsManager.instrumentChanged.connect(
            self.noteBlockArea.changeSelectionInstrument
        )

    def initFile(self):
        Actions.openSongAction.triggered.connect(self.loadSong)
        Actions.saveSongAction.triggered.connect(self.saveSong)
        Actions.saveSongAsAction.triggered.connect(self.saveSong)

    @QtCore.pyqtSlot()
    def loadSong(self):

        filename = getLoadSongDialog()
        if not filename:
            return

        song = Song.from_file(filename)
        self.noteBlockArea.loadNoteData(song.notes)
        self.layerArea.loadLayerData(song.layers)
        self.setCurrentInstrumentActionsManager.currentInstrument = 0

    @QtCore.pyqtSlot()
    def saveSong(self):
        header = {}
        notes = self.noteBlockArea.getNoteData()
        layers = self.layerArea.getLayerData()
        instruments = []

        song = Song(header, notes, layers, instruments)
        song.save()
