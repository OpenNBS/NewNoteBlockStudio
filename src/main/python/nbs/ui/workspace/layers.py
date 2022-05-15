import qtawesome as qta
from PyQt5 import QtCore, QtWidgets

from .constants import *

__all__ = ["LayerArea"]


class VerticalScrollArea(QtWidgets.QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup()

    def setup(self):
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Resize:
            obj.setMinimumWidth(self.minimumSizeHint().width() + 40)
        return super().eventFilter(obj, event)


class LayerBar(QtWidgets.QToolBar):
    """A single layer bar."""

    volumeChanged = QtCore.pyqtSignal(int, int)
    panningChanged = QtCore.pyqtSignal(int, int)
    lockChanged = QtCore.pyqtSignal(int, bool)
    soloChanged = QtCore.pyqtSignal(int, bool)
    selectAllClicked = QtCore.pyqtSignal(int)
    addClicked = QtCore.pyqtSignal(int)
    removeClicked = QtCore.pyqtSignal(int)
    shiftUpClicked = QtCore.pyqtSignal(int)
    shiftDownClicked = QtCore.pyqtSignal(int)

    def __init__(
        self,
        id,
        height,
        name="",
        volume=100,
        panning=100,
        locked=False,
        solo=False,
        parent=None,
    ):
        super().__init__(parent)
        self.id = id
        self.name = name
        self.volume = volume
        self.panning = panning
        self.locked = locked
        self.solo = solo
        self.icons = self.initIcons()
        self.initUI(height)

    def initIcons(self):
        return {
            "volume": qta.icon("mdi.volume-high"),
            "stereo": qta.icon("mdi.equalizer"),
            "lock": qta.icon(
                "mdi.lock-outline", selected="mdi.lock-open-variant-outline"
            ),
            "solo": qta.icon("mdi.exclamation", selected="mdi.exclamation-thick"),
            "select_all": qta.icon("mdi.select-all"),
            "insert": qta.icon("mdi.plus-circle-outline"),  # mdi.plus-box
            "remove": qta.icon("mdi.delete-outline"),  # mdi.trash-can
            "shift_up": qta.icon("mdi.arrow-up-bold"),
            "shift_down": qta.icon("mdi.arrow-down-bold"),
        }

    def initUI(self, height):
        self.setIconSize(QtCore.QSize(20, 24))
        self.setFixedHeight(height - 2)
        self.setMaximumWidth(342)  # TODO: calculate instead of hardcode
        sizePolicy = self.sizePolicy()
        sizePolicy.setRetainSizeWhenHidden(True)
        self.setSizePolicy(sizePolicy)
        self.addFrame()
        self.addContents()

    def addFrame(self):
        self.layout = QtWidgets.QHBoxLayout()
        self.layout.setContentsMargins(5, 0, 5, 0)
        self.layout.addWidget(self)
        self.frame = QtWidgets.QFrame()
        self.frame.setFrameStyle(QtWidgets.QFrame.Panel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setLineWidth(1)
        self.frame.setLayout(self.layout)

    def addContents(self):
        self.nameBox = QtWidgets.QLineEdit()
        self.nameBox.setFixedSize(76, 16)
        self.nameBox.setPlaceholderText("Layer {}".format(self.id + 1))
        self.addWidget(self.nameBox)

        self.volumeDial = QtWidgets.QDial()
        self.volumeDial.setNotchesVisible(True)
        self.volumeDial.setNotchTarget(3.5)
        self.volumeDial.setSingleStep(10)
        self.volumeDial.setRange(0, 100)
        self.volumeDial.setValue(100)
        self.volumeDial.setNotchesVisible(True)
        self.volumeDial.setContentsMargins(0, 0, 0, 0)
        self.volumeDial.setMaximumWidth(32)
        self.addWidget(self.volumeDial)

        self.panningDial = QtWidgets.QDial()
        self.panningDial.setNotchesVisible(True)
        self.panningDial.setNotchTarget(3.5)
        self.panningDial.setSingleStep(10)
        self.panningDial.setRange(-100, 100)
        self.panningDial.setValue(0)
        self.panningDial.setContentsMargins(0, 0, 0, 0)
        self.panningDial.setMaximumWidth(32)
        self.addWidget(self.panningDial)

        # self.addAction(self.icons["volume"], "Volume")
        # self.addAction(self.icons["stereo"], "Stereo panning")
        lockAction = self.addAction(self.icons["lock"], "Lock this layer")
        lockAction.setCheckable(True)
        lockAction.triggered.connect(
            lambda checked: self.lockChanged.emit(self.id, checked)
        )

        soloAction = self.addAction(
            self.icons["solo"],
            "Solo this layer",
        )
        soloAction.setCheckable(True)
        soloAction.setCheckable(True)
        soloAction.triggered.connect(
            lambda checked: self.lockChanged.emit(self.id, checked)
        )

        selectAllAction = self.addAction(
            self.icons["select_all"],
            "Select all note blocks in this layer",
            lambda: self.selectAllClicked.emit(self.id),
        )
        addAction = self.addAction(
            self.icons["insert"],
            "Add empty layer here",
            lambda: self.addClicked.emit(self.id),
        )
        removeAction = self.addAction(
            self.icons["remove"],
            "Remove this layer",
            lambda: self.removeClicked.emit(self.id),
        )
        shiftUpAction = self.addAction(
            self.icons["shift_up"],
            "Shift layer up",
            lambda: self.shiftUpClicked.emit(self.id),
        )
        shiftDownAction = self.addAction(
            self.icons["shift_down"],
            "Shift layer down",
            lambda: self.shiftDownClicked.emit(self.id),
        )

    @QtCore.pyqtSlot(float)
    def changeScale(self, factor):
        self.setFixedHeight(factor * BLOCK_SIZE - 2)
        if factor < 0.5:
            self.hide()
        else:
            self.show()


class LayerArea(VerticalScrollArea):

    layerVolumeChanged = QtCore.pyqtSignal(int, int)
    layerPanningChanged = QtCore.pyqtSignal(int, int)
    layerLockChanged = QtCore.pyqtSignal(int, bool)
    layerSoloChanged = QtCore.pyqtSignal(int, bool)
    layerSelected = QtCore.pyqtSignal(int)
    layerAdded = QtCore.pyqtSignal(int)
    layerRemoved = QtCore.pyqtSignal(int)
    layersSwapped = QtCore.pyqtSignal(int, int)

    changeScale = QtCore.pyqtSignal(float)

    def __init__(self, layerCount=200, parent=None):
        # TODO: do we need a default layer number? Should it be 200?
        super().__init__(parent)
        self.layerCount = layerCount
        self.layers = []
        self.layerHeight = BLOCK_SIZE
        self.initUI()

    def initUI(self):
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(5, 0, 0, 0)
        self.container = QtWidgets.QWidget()
        self.container.setLayout(self.layout)
        self.container.setContentsMargins(0, 0, 0, 0)

        # self.updateLayerCount(100)
        for i in range(self.layerCount):
            layer = LayerBar(i, self.layerHeight)
            self.layout.addWidget(layer.frame)
            self.layers.append(layer)
            self.changeScale.connect(layer.changeScale)

            layer.volumeChanged.connect(self.changeLayerVolume)
            layer.panningChanged.connect(self.changeLayerPanning)
            layer.lockChanged.connect(self.changeLayerLock)
            layer.soloChanged.connect(self.changeLayerSolo)
            layer.selectAllClicked.connect(self.layerSelected)
            layer.addClicked.connect(self.addLayer)
            layer.removeClicked.connect(self.removeLayer)
            layer.shiftUpClicked.connect(self.shiftLayerUp)
            layer.shiftDownClicked.connect(self.shiftLayerDown)

        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setMaximumWidth(342)  # TODO: calculate instead of hardcode
        self.setWidget(self.container)

    def wheelEvent(self, event):
        # Prevent scrolling with the mouse wheel
        if event.type() == QtCore.QEvent.Wheel:
            event.ignore()

    @QtCore.pyqtSlot(int)
    def updateLayerHeight(self, height):
        self.layerHeight = height

    @QtCore.pyqtSlot(int, int)
    def updateLayerCount(self, newSize):
        count = newSize // BLOCK_SIZE
        if self.layerCount < count:
            while self.layerCount < count:
                self.layerCount += 1
                layer = LayerBar(self.layerCount, self.layerHeight)
                print("ADDING")
                self.layout.addWidget(layer.frame)
                self.layers.append(layer)
                self.changeScale.connect(layer.changeScale)
        else:
            while self.layerCount > count:
                self.layerCount -= 1
                i = self.layout.count()
                print("REMOVING", i)
                self.layout.takeAt(i)

    ######## FEATURES ########

    @QtCore.pyqtSlot(int, int)
    def changeLayerVolume(self, id: int, volume: int):
        self.layers[id].setVolume(volume)
        self.layerVolumeChanged.emit(id, volume)

    @QtCore.pyqtSlot(int, int)
    def changeLayerPanning(self, id: int, panning: int):
        self.layers[id].setPanning(panning)
        self.layerPanningChanged.emit(id, panning)

    @QtCore.pyqtSlot(int, bool)
    def changeLayerLock(self, id: int, lock: bool):
        self.layers[id].setLock(lock)
        self.layerLockChanged.emit(id, lock)

    @QtCore.pyqtSlot(int, bool)
    def changeLayerSolo(self, id: int, solo: bool):
        self.layers[id].setSolo(solo)
        self.layerSoloChanged.emit(id, solo)

    @QtCore.pyqtSlot(int)
    def addLayer(self, pos: int):
        newLayer = LayerBar(pos, BLOCK_SIZE)
        self.layers.insert(pos, newLayer)
        self.layerAdded.emit(pos)

    @QtCore.pyqtSlot(int)
    def removeLayer(self, pos: int):
        self.layers.pop(pos)
        self.layerRemoved.emit(pos)

    def swapLayers(self, id1, id2):
        temp = self.layers[id1]
        self.layers[id1] = self.layers[id2]
        self.layers[id2] = temp
        self.layersSwapped.emit(id1, id2)

    QtCore.pyqtSlot(int)

    def shiftLayerUp(self, id):
        if id == 0:
            return
        self.swapLayers(id, id - 1)

    QtCore.pyqtSlot(int)

    def shiftLayerDown(self, id):
        if id == len(self.layers) - 1:
            return
        self.swapLayers(id, id + 1)
