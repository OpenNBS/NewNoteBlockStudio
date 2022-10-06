from pathlib import Path

from PyQt5 import QtCore, QtWidgets

from nbs.controller.instrument import InstrumentController
from nbs.controller.layer import LayerController
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
from nbs.ui.dialog.instrument_settings import InstrumentSettingsDialog
from nbs.ui.file import getLoadSongDialog
from nbs.ui.menus import MenuBar
from nbs.ui.status_bar import StatusBar
from nbs.ui.toolbar import ToolBar
from nbs.ui.workspace import *
from nbs.ui.workspace.layers import LayerArea
from nbs.ui.workspace.note_blocks import NoteBlockArea
from nbs.ui.workspace.piano import HorizontalAutoScrollArea, PianoWidget
from nbs.ui.workspace.time_bar import TimeBar
from nbs.ui.workspace.workspace import Workspace


class MainWindow(QtWidgets.QMainWindow):

    soundLoadRequested = QtCore.pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layers = []
        self.setWindowTitle("Minecraft Note Block Studio")
        self.setMinimumSize(854, 480)
        self.initAudio()
        self.initControllers()
        self.initUI()
        self.initNoteBlocks()
        self.initLayers()
        self.initTimeBar()
        self.initPiano()
        self.initInstruments()
        self.initFile()
        self.initDialogs()

    def initAudio(self):
        self.audioThread = QtCore.QThread()
        self.audioEngine = AudioEngine()
        self.audioEngine.moveToThread(self.audioThread)
        self.audioThread.started.connect(self.audioEngine.run)
        QtCore.QCoreApplication.instance().aboutToQuit.connect(self.audioEngine.stop)
        self.audioEngine.finished.connect(self.audioThread.quit)
        self.soundLoadRequested.connect(self.audioEngine.loadSounds)
        self.audioThread.start()

    def initControllers(self):
        self.playbackController = PlaybackController()
        self.instrumentController = InstrumentController(default_instruments)
        self.layerManager = LayerController(self.layers)

    def initUI(self):
        self.menuBar = MenuBar()
        self.toolBar = ToolBar()
        # self.instrumentBar = InstrumentToolBar()
        self.statusBar = StatusBar()

        self.setMenuBar(self.menuBar)
        self.addToolBar(self.toolBar)
        # self.addToolBar(self.instrumentBar)
        self.setStatusBar(self.statusBar)

        self.noteBlockArea = NoteBlockArea(layers=self.layers)
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
        Actions.deleteAction.triggered.connect(self.noteBlockArea.deleteSelection)

        Actions.selectAllAction.triggered.connect(self.noteBlockArea.selectAll)
        Actions.deselectAllAction.triggered.connect(self.noteBlockArea.deselectAll)
        Actions.invertSelectionAction.triggered.connect(
            self.noteBlockArea.invertSelection
        )
        Actions.selectAllLeftAction.triggered.connect(self.noteBlockArea.selectAllLeft)
        Actions.selectAllRightAction.triggered.connect(
            self.noteBlockArea.selectAllRight
        )
        Actions.expandSelectionAction.triggered.connect(
            self.noteBlockArea.expandSelection
        )
        Actions.compressSelectionAction.triggered.connect(
            self.noteBlockArea.compressSelection
        )

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
            lambda ins, key: self.audioEngine.playSound(ins, 1.0, key - 45, 0)
        )
        self.noteBlockArea.tickPlayed.connect(
            lambda sounds: self.audioEngine.playSounds(
                ((ins, vol, key - 45, pan) for ins, key, vol, pan in sounds)
            )
        )

    def initLayers(self):
        lm = self.layerManager
        la = self.layerArea
        nba = self.noteBlockArea

        # Connect widget to note block area (the manager isn't aware of selections,
        # so the connection can be direct)
        la.layerSelectRequested.connect(nba.selectAllInLayer)

        # Connect note block area to manager (to inform it of changes in the layer count)
        nba.sceneSizeChanged.connect(lambda _, height: lm.updateLayerCount(height))

        # Connect widget to manager
        la.layerAddRequested.connect(lm.addLayer)
        la.layerRemoveRequested.connect(lm.removeLayer)
        la.layerMoveRequested.connect(lm.moveLayer)
        la.layerNameChangeRequested.connect(lm.setLayerName)
        la.layerVolumeChangeRequested.connect(lm.setLayerVolume)
        la.layerPanningChangeRequested.connect(lm.setLayerPanning)
        la.layerLockChangeRequested.connect(lm.setLayerLock)
        la.layerSoloChangeRequested.connect(lm.setLayerSolo)

        # Connect manager to widget
        lm.layerAdded.connect(la.addLayer)
        lm.layerRemoved.connect(la.removeLayer)
        lm.layerNameChanged.connect(la.changeLayerName)
        lm.layerLockChanged.connect(la.changeLayerLock)
        lm.layerSoloChanged.connect(la.changeLayerSolo)
        lm.layerVolumeChanged.connect(la.changeLayerVolume)
        lm.layerPanningChanged.connect(la.changeLayerPanning)

        # Connect manager to note block area
        lm.layerAdded.connect(nba.addLayer)
        lm.layerRemoved.connect(nba.removeLayer)
        lm.layerSwapped.connect(nba.shiftLayers)
        lm.layerLockChanged.connect(nba.setLayerLock)
        lm.layerSoloChanged.connect(nba.setLayerSolo)

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
                1.0,
                key - 45,
                0,
            )
        )

    def initInstruments(self):

        self.instrumentController = InstrumentController(default_instruments)

        sounds = []
        for ins in default_instruments:
            sound_path = appctxt.get_resource(Path("sounds", ins.sound_path))
            sounds.append(sound_path)

        self.soundLoadRequested.emit(sounds)

        instrumentList = self.instrumentController.instruments

        # Set current instrument actions
        self.setCurrentInstrumentActionsManager.updateActions(instrumentList)
        self.setCurrentInstrumentActionsManager.instrumentChanged.connect(
            # TODO: connect this to future InstrumentManager object that will notify widgets
            self.noteBlockArea.setCurrentInstrument
            # self.centralWidget().workspace.piano.setValidRange(ins)
        )
        self.setCurrentInstrumentActionsManager.currentInstrument = 0

        self.toolBar.populateInstruments()
        self.toolBar.instrumentButtonPressed.connect(
            lambda id_: self.audioEngine.playSound(
                id_, 1.0, self.piano.activeKey - 45, 0
            )
        )

        # 'Change instrument...' actions
        self.changeInstrumentActionsManager.updateActions(instrumentList)
        self.changeInstrumentActionsManager.instrumentChanged.connect(
            self.noteBlockArea.changeSelectionInstrument
        )

    def initFile(self):
        Actions.openSongAction.triggered.connect(self.loadSong)
        Actions.saveSongAction.triggered.connect(self.saveSong)
        Actions.saveSongAsAction.triggered.connect(self.saveSong)

    def initDialogs(self):
        # Instrument settings
        self.instrumentSettingsDialog = InstrumentSettingsDialog(
            self.instrumentController.instruments
        )
        Actions.instrumentSettingsAction.triggered.connect(
            self.instrumentSettingsDialog.show
        )
        self.instrumentSettingsDialog.instrumentAddRequested.connect(
            self.instrumentController.createInstrument
        )
        self.instrumentController.instrumentAdded.connect(
            self.instrumentSettingsDialog.addInstrument
        )

    @QtCore.pyqtSlot()
    def loadSong(self):

        filename = getLoadSongDialog()
        if not filename:
            return

        song = Song.from_file(filename)
        self.noteBlockArea.loadNoteData(song.notes)
        self.layerManager.resetLayers()
        self.layerManager.loadLayers(song.layers)
        self.setCurrentInstrumentActionsManager.currentInstrument = 0

    @QtCore.pyqtSlot()
    def saveSong(self):
        header = {}
        notes = self.noteBlockArea.getNoteData()
        layers = self.layerArea.getLayerData()
        instruments = []

        song = Song(header, notes, layers, instruments)
        song.save()
