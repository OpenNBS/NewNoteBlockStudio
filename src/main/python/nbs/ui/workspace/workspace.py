from PyQt5 import QtCore, QtWidgets

from .constants import *

__all__ = ["CentralArea"]


class Workspace(QtWidgets.QSplitter):
    """
    A splitter holding a layer area on the left and a note
    block area on the right.
    """

    def __init__(
        self,
        noteBlockWidget: QtCore.QObject,
        layerWidget: QtCore.QObject,
        timeBar=QtCore.QObject,
        parent=None,
    ):
        super().__init__(parent)
        self.noteBlockWidget = noteBlockWidget
        self.layerWidget = layerWidget
        self.timeBar = timeBar

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
        self.noteBlockWidget.view.playbackManager.playbackPositionChanged.connect(
            self.timeBar.currentTimeChanged_
        )
        self.noteBlockWidget.sceneSizeChanged.connect(
            lambda _, height: self.layerWidget.updateLayerCount(height // BLOCK_SIZE)
        )
        self.timeBar.tempoChanged.connect(self.noteBlockWidget.view.tempoChanged)

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
    def __init__(
        self,
        workspace: QtCore.QObject,
        pianoWidget: QtCore.QObject,
        pianoContainer: QtCore.QObject,
        parent=None,
    ):
        super().__init__(parent)
        self.workspace = workspace
        self.workspace.setParent(self)

        self.pianoWidget = pianoWidget
        self.workspace.setParent(self)
        self.pianoContainer = pianoContainer
        self.pianoContainer.setParent(self)
        self.pianoContainer.setWidget(self.pianoWidget)

        self.initUI()

    def initUI(self):
        self.setOrientation(QtCore.Qt.Vertical)
        self.setHandleWidth(2)
        self.addWidget(self.workspace)
        self.addWidget(self.pianoContainer)
        # reserve just enough space for piano and let workspace occupy the rest
        pianoHeight = self.pianoWidget.height()
        self.setSizes([1, pianoHeight])
        self.handle(1).setEnabled(False)  # make handle unmovable
        self.setStretchFactor(0, 1)  # set workspace to stretch
        self.setStretchFactor(1, 0)  # set piano to NOT stretch
        # TODO: perhaps a QVBoxLayout is more appropriate here?
