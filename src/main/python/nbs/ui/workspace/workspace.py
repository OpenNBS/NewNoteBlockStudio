from PyQt5 import QtCore, QtWidgets

from .constants import *
from .layers import LayerArea
from .note_blocks import NoteBlockArea
from .piano import PianoScroll
from .time_bar import TimeBar

__all__ = ["CentralArea"]


class Workspace(QtWidgets.QSplitter):
    """
    A splitter holding a layer area on the left and a note
    block area on the right.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layerWidget = LayerArea()
        self.noteBlockWidget = NoteBlockArea()
        self.timeBar = TimeBar()

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.timeBar)
        layout.addWidget(self.layerWidget)

        # fill vertical space taken by horizontal scrollbar
        spacer = QtWidgets.QWidget()
        spacer.setFixedHeight(SCROLL_BAR_SIZE)
        layout.addWidget(spacer)

        leftPanel = QtWidgets.QWidget()
        leftPanel.setMaximumWidth(self.layerWidget.maximumWidth())
        leftPanel.setLayout(layout)

        self.addWidget(leftPanel)
        self.addWidget(self.noteBlockWidget.view)
        self.setHandleWidth(2)

        self.noteBlockWidget.view.verticalScrollBar().valueChanged.connect(
            self.layerWidget.verticalScrollBar().setValue
        )
        self.noteBlockWidget.view.scaleChanged.connect(
            lambda x: self.layerWidget.updateLayerHeight(x * BLOCK_SIZE)
        )
        self.noteBlockWidget.view.markerMoved.connect(self.timeBar.currentTimeChanged_)
        self.noteBlockWidget.sceneSizeChanged.connect(
            lambda _, height: self.layerWidget.updateLayerCount(height // BLOCK_SIZE)
        )
        self.timeBar.tempoChanged.connect(self.noteBlockWidget.view.ruler.setTempo)

        # Layer signals
        self.layerWidget.layerVolumeChanged.connect(self.noteBlockWidget.setLayerVolume)
        self.layerWidget.layerPanningChanged.connect(
            self.noteBlockWidget.setLayerPanning
        )
        self.layerWidget.layerLockChanged.connect(self.noteBlockWidget.setLayerLock)
        self.layerWidget.layerSoloChanged.connect(self.noteBlockWidget.setLayerSolo)
        self.layerWidget.layerSelected.connect(self.noteBlockWidget.selectAllInLayer)
        self.layerWidget.layerAdded.connect(self.noteBlockWidget.addLayer)
        self.layerWidget.layerRemoved.connect(self.noteBlockWidget.removeLayer)
        self.layerWidget.layerMoved.connect(self.noteBlockWidget.shiftLayers)

    def resetWorkspace(self):
        self.layerWidget.initUI()
        self.noteBlockWidget.clear()

    def loadSong(self, notes, layers):
        pass
        # TODO: load notes to NoteBlockArea and layers to LayerArea here


class CentralArea(QtWidgets.QSplitter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.workspace = Workspace()
        self.piano = PianoScroll(keyCount=88, offset=9, validRange=(33, 57))
        self.initUI()

    def initUI(self):
        self.setOrientation(QtCore.Qt.Vertical)
        self.setHandleWidth(2)
        self.addWidget(self.workspace)
        self.addWidget(self.piano)
        # reserve just enough space for piano and let workspace occupy the rest
        pianoHeight = self.piano.piano.height()
        self.setSizes([1, pianoHeight])
        self.handle(1).setEnabled(False)  # make handle unmovable
        self.setStretchFactor(0, 1)  # set workspace to stretch
        self.setStretchFactor(1, 0)  # set piano to NOT stretch
        # TODO: perhaps a QVBoxLayout is more appropriate here?
        self.piano.piano.activeKeyChanged.connect(
            self.workspace.noteBlockWidget.setActiveKey
        )
