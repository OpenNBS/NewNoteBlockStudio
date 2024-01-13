from pathlib import Path

from PyQt5 import QtCore, QtGui, QtWidgets

from nbs.controller.clipboard import ClipboardController
from nbs.controller.instrument import InstrumentController
from nbs.controller.layer import LayerController
from nbs.controller.playback import PlaybackController
from nbs.controller.song import SongController
from nbs.core.audio import AudioEngine
from nbs.core.context import appctxt
from nbs.core.data import Song, default_instruments
from nbs.core.file import load_song, save_song
from nbs.ui.actions import (
    Actions,
    ChangeInstrumentActionManager,
    SetCurrentInstrumentActionManager,
)
from nbs.ui.dialog.instrument_settings import InstrumentSettingsDialog
from nbs.ui.file import getLoadSongDialog, getSaveSongDialog
from nbs.ui.menus import EditMenu, MenuBar
from nbs.ui.status_bar import StatusBar
from nbs.ui.toolbar import *
from nbs.ui.workspace import *
from nbs.ui.workspace.layers import LayerArea
from nbs.ui.workspace.note_blocks import NoteBlockArea
from nbs.ui.workspace.piano import HorizontalAutoScrollArea, PianoWidget
from nbs.ui.workspace.time_bar import TimeBar
from nbs.ui.workspace.workspace import Workspace


class MainWindow(QtWidgets.QMainWindow):
    soundLoadRequested = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layers = []
        self.instruments = [*default_instruments]
        self.clipboard = QtGui.QGuiApplication.clipboard()
        self.setWindowTitle("Minecraft Note Block Studio")
        self.setMinimumSize(854, 480)
        self.initAudio()
        self.initControllers()
        self.initUI()
        self.initDialogs()
        self.initNoteBlocks()
        self.initLayers()
        self.initTimeBar()
        self.initPiano()
        self.initInstruments()
        self.initFile()

    def initAudio(self):
        self.audioThread = QtCore.QThread()
        self.audioEngine = AudioEngine()
        self.audioEngine.moveToThread(self.audioThread)
        self.audioThread.started.connect(self.audioEngine.run)
        QtCore.QCoreApplication.instance().aboutToQuit.connect(self.audioEngine.stop)
        self.audioEngine.finished.connect(self.audioThread.quit)
        self.soundLoadRequested.connect(self.audioEngine.loadSound)
        self.audioThread.start()

    def initControllers(self):
        self.playbackController = PlaybackController()
        self.instrumentController = InstrumentController(self.instruments)
        self.layerManager = LayerController(self.layers)
        self.songController = SongController(
            self.layerManager, self.instrumentController, self.playbackController
        )
        self.clipboardManager = ClipboardController(self.clipboard)

    def initUI(self):
        self.currentInstrumentActionManager = SetCurrentInstrumentActionManager()
        self.changeInstrumentActionManager = ChangeInstrumentActionManager()

        self.menuBar_ = MenuBar(
            changeInstrumentActions=self.changeInstrumentActionManager.actions,
            setCurrentInstrumentActions=self.currentInstrumentActionManager.actions,
        )
        self.playbackToolBar = PlaybackToolBar()
        self.instrumentBar = InstrumentToolBar()
        self.editToolBar = EditToolBar()

        self.statusBar = StatusBar()

        self.setMenuBar(self.menuBar_)
        self.addToolBar(self.playbackToolBar)
        self.addToolBar(self.instrumentBar)
        self.addToolBar(self.editToolBar)
        self.setStatusBar(self.statusBar)

        self.audioEngine.soundCountUpdated.connect(self.statusBar.setSoundCount)

        self.noteBlockAreaCtxMenu = EditMenu(isContextMenu=True)
        self.noteBlockArea = NoteBlockArea(
            layers=self.layers, menu=self.noteBlockAreaCtxMenu
        )
        self.layerArea = LayerArea()
        self.timeBar = TimeBar()
        self.piano = PianoWidget(keyCount=88, offset=9, validRange=(33, 57))
        self.pianoContainer = HorizontalAutoScrollArea()

        self.workspace = Workspace(self.noteBlockArea, self.layerArea, self.timeBar)
        self.centralArea = CentralArea(self.workspace, self.piano, self.pianoContainer)

        self.setCentralWidget(self.centralArea)

    def initNoteBlocks(self):
        # Selection
        self.noteBlockArea.blockCountChanged.connect(Actions.setBlockCount)
        self.noteBlockArea.selectionChanged_.connect(Actions.setSelectionStatus)

        Actions.cutAction.triggered.connect(self.noteBlockArea.cutSelection)
        Actions.copyAction.triggered.connect(self.noteBlockArea.copySelection)
        Actions.deleteAction.triggered.connect(self.noteBlockArea.deleteSelection)

        Actions.selectAllAction.triggered.connect(self.noteBlockArea.selectAll)
        Actions.deselectAllAction.triggered.connect(self.noteBlockArea.deselectAll)
        Actions.invertSelectionAction.triggered.connect(
            self.noteBlockArea.invertSelection
        )
        self.noteBlockArea.selectAllLeftActionEnabled.connect(
            Actions.selectAllLeftAction.setEnabled
        )
        self.noteBlockArea.selectAllRightActionEnabled.connect(
            Actions.selectAllRightAction.setEnabled
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

        # Clipboard
        self.noteBlockArea.selectionCopied.connect(self.clipboardManager.setContent)
        Actions.pasteAction.triggered.connect(
            lambda: self.noteBlockArea.pasteSelection(
                self.clipboardManager.getContent()
            )
        )
        self.clipboardManager.clipboardCountChanged.connect(
            lambda length: Actions.setClipboard(length > 0)
        )

        # Playback
        Actions.playPauseAction.triggered.connect(self.playbackController.setPlaying)
        Actions.stopAction.triggered.connect(self.playbackController.stop)

        self.playbackController.callback = self.noteBlockArea.view.setPlaybackPosition
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
        nba.sceneSizeChanged.connect(
            lambda _, height: lm.setWorkspaceLayerCount(height)
        )
        lm.populatedLayerCountChanged.connect(nba.setMinimumLayerCount)
        lm.visibleLayerCountChanged.connect(la.setLayerCount)

        # Connect widget to manager
        la.layerAddRequested.connect(lm.addLayer)
        la.layerRemoveRequested.connect(lm.removeLayer)
        la.layerMoveRequested.connect(lm.swapLayers)
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
        lm.layerSwapped.connect(la.swapLayers)

        # Connect manager to note block area
        lm.layerAdded.connect(nba.addLayer)
        lm.layerRemoved.connect(nba.removeLayer)
        lm.layerSwapped.connect(nba.swapLayers)
        lm.layerLockChanged.connect(nba.setLayerLock)
        lm.layerSoloChanged.connect(nba.setLayerSolo)

    def initTimeBar(self):
        tb = self.timeBar
        pc = self.playbackController

        tb.tempoChangeRequested.connect(pc.setTempo)
        pc.tempoChanged.connect(tb.setTempo)
        pc.playbackPositionChanged.connect(tb.setCurrentTime)
        pc.songLengthChanged.connect(tb.setSongLength)
        pc.tempoChanged.connect(self.noteBlockArea.view.setTempo)

        self.noteBlockArea.songLengthChanged.connect(pc.setSongLength)

    def initPiano(self):
        # Set active workspace key
        self.piano.activeKeyChanged.connect(self.noteBlockArea.setActiveKey)
        self.piano.activeKey = 39

        # Sounds
        self.piano.activeKeyChanged.connect(
            lambda key: self.audioEngine.playSound(
                self.instrumentController.currentInstrument,
                1.0,
                key - 45,
                0,
            )
        )

        # Playback
        # TODO: NoteBlockArea sends key and pitch combined into a single float. Needs to be split
        self.noteBlockArea.tickPlayed.connect(
            lambda sounds: self.piano.playKeys((int(key)) for _, key, _, _ in sounds)
        )

    def initInstruments(self):
        control = self.instrumentController
        dialog = self.instrumentSettingsDialog
        setInsManager = self.currentInstrumentActionManager
        changeInsManager = self.changeInstrumentActionManager

        # Audio engine
        for ins in default_instruments:
            sound_path = appctxt.get_resource(Path("sounds", ins.sound_path))
            self.soundLoadRequested.emit(sound_path)

        control.instrumentSoundLoadRequested.connect(self.soundLoadRequested)

        # Set up initial state
        control.setCurrentInstrument(0)
        setInsManager.updateInstruments(self.instruments)

        self.instrumentBar.populateInstruments(setInsManager.actions)

        # Set current instrument actions
        setInsManager.currentInstrumentChangeRequested.connect(
            control.setCurrentInstrument
        )
        control.instrumentListUpdated.connect(setInsManager.updateInstruments)

        # 'Change instrument...' actions
        changeInsManager.instrumentChangeRequested.connect(control.setCurrentInstrument)
        control.currentInstrumentChanged.connect(setInsManager.setCurrentInstrument)

        # Instrument bar
        self.instrumentBar.instrumentButtonPressed.connect(
            lambda id_: self.audioEngine.playSound(
                id_, 1.0, self.piano.activeKey - 45, 0
            )
        )
        control.instrumentListUpdated.connect(
            lambda: self.instrumentBar.populateInstruments(setInsManager.actions)
        )

        # Menus are populated on demand

        # Note block area
        control.currentInstrumentChanged.connect(
            self.noteBlockArea.setCurrentInstrument
        )

        # Instrument Settings dialog
        dialog.instrumentAddRequested.connect(control.createInstrument)
        dialog.instrumentRemoveRequested.connect(control.removeInstrument)
        dialog.instrumentNameChangeRequested.connect(control.setInstrumentName)
        dialog.instrumentSoundFileChangeRequested.connect(control.setInstrumentSound)
        dialog.instrumentKeyChangeRequested.connect(control.setInstrumentKey)
        dialog.instrumentPressChangeRequested.connect(control.setInstrumentPress)
        dialog.instrumentShiftRequested.connect(control.swapInstruments)
        control.instrumentAdded.connect(dialog.addInstrument)
        control.instrumentRemoved.connect(dialog.removeInstrument)
        control.instrumentChanged.connect(dialog.editInstrument)
        control.instrumentSwapped.connect(dialog.shiftInstrument)

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

    @QtCore.pyqtSlot()
    def loadSong(self):
        filename = getLoadSongDialog()
        if not filename:
            return

        song = load_song(filename)
        self.noteBlockArea.loadNoteData(song.notes)
        self.songController.loadSong(song)
        self.instrumentController.setCurrentInstrument(0)

    @QtCore.pyqtSlot()
    def saveSong(self):
        filename = getSaveSongDialog()
        if not filename:
            return
        save_song(self.songController.song, filename)
