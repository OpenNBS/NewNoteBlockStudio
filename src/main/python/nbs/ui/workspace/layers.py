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


class LayerBar(QtWidgets.QFrame):
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

        self.setFrameStyle(QtWidgets.QFrame.Panel)
        self.setFrameShadow(QtWidgets.QFrame.Raised)
        self.setLineWidth(1)
        self.setFixedHeight(height - 2)

        toolbar = QtWidgets.QToolBar()
        toolbar.setIconSize(QtCore.QSize(16, 24))

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(5, 0, 5, 0)
        layout.addWidget(toolbar)
        self.setLayout(layout)

        self.nameBox = QtWidgets.QLineEdit()
        self.nameBox.setFixedSize(76, 16)
        self.nameBox.setPlaceholderText("Layer {}".format(self.id + 1))
        toolbar.addWidget(self.nameBox)

        self.volumeDial = QtWidgets.QDial()
        self.volumeDial.setNotchesVisible(True)
        self.volumeDial.setNotchTarget(3.5)
        self.volumeDial.setSingleStep(10)
        self.volumeDial.setRange(0, 100)
        self.volumeDial.setValue(100)
        self.volumeDial.setNotchesVisible(True)
        self.volumeDial.setContentsMargins(0, 0, 0, 0)
        self.volumeDial.setMaximumWidth(32)
        toolbar.addWidget(self.volumeDial)

        self.panningDial = QtWidgets.QDial()
        self.panningDial.setNotchesVisible(True)
        self.panningDial.setNotchTarget(3.5)
        self.panningDial.setSingleStep(10)
        self.panningDial.setRange(-100, 100)
        self.panningDial.setValue(0)
        self.panningDial.setContentsMargins(0, 0, 0, 0)
        self.panningDial.setMaximumWidth(32)
        toolbar.addWidget(self.panningDial)

        # self.addAction(self.icons["volume"], "Volume")
        # self.addAction(self.icons["stereo"], "Stereo panning")
        lockAction = toolbar.addAction(self.icons["lock"], "Lock this layer")
        lockAction.setCheckable(True)
        lockAction.triggered.connect(
            lambda checked: self.lockChanged.emit(self.id, checked)
        )

        soloAction = toolbar.addAction(
            self.icons["solo"],
            "Solo this layer",
        )
        soloAction.setCheckable(True)
        soloAction.triggered.connect(
            lambda checked: self.lockChanged.emit(self.id, checked)
        )

        selectAllAction = toolbar.addAction(
            self.icons["select_all"],
            "Select all note blocks in this layer",
            lambda: self.selectAllClicked.emit(self.id),
        )
        addAction = toolbar.addAction(
            self.icons["insert"],
            "Add empty layer here",
            lambda: self.addClicked.emit(self.id),
        )
        removeAction = toolbar.addAction(
            self.icons["remove"],
            "Remove this layer",
            lambda: self.removeClicked.emit(self.id),
        )
        shiftUpAction = toolbar.addAction(
            self.icons["shift_up"],
            "Shift layer up",
            lambda: self.shiftUpClicked.emit(self.id),
        )
        shiftDownAction = toolbar.addAction(
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

    def setId(self, newId: int):
        print(newId)
        self.id = newId
        self.nameBox.setPlaceholderText("Layer {}".format(self.id + 1))


class LayerArea(VerticalScrollArea):

    layerVolumeChanged = QtCore.pyqtSignal(int, int)
    layerPanningChanged = QtCore.pyqtSignal(int, int)
    layerLockChanged = QtCore.pyqtSignal(int, bool)
    layerSoloChanged = QtCore.pyqtSignal(int, bool)
    layerSelected = QtCore.pyqtSignal(int)
    layerAdded = QtCore.pyqtSignal(int)
    layerRemoved = QtCore.pyqtSignal(int)
    layerMoved = QtCore.pyqtSignal(int, int)

    changeScale = QtCore.pyqtSignal(float)

    def __init__(self, layerCount=200, parent=None):
        # TODO: do we need a default layer number? Should it be 200?
        super().__init__(parent)
        self.layerCount = layerCount
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
            self.layout.addWidget(layer)
            self.changeScale.connect(layer.changeScale)

            layer.volumeChanged.connect(self.layerVolumeChanged)
            layer.panningChanged.connect(self.layerPanningChanged)
            layer.lockChanged.connect(self.layerLockChanged)
            layer.soloChanged.connect(self.layerSoloChanged)
            layer.selectAllClicked.connect(self.layerSelected)
            layer.addClicked.connect(self.addLayer)
            layer.removeClicked.connect(self.removeLayer)
            layer.shiftUpClicked.connect(self.shiftLayerUp)
            layer.shiftDownClicked.connect(self.shiftLayerDown)

        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setMaximumWidth(324)  # TODO: calculate instead of hardcode
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
                self.layout.addWidget(layer)
                self.changeScale.connect(layer.changeScale)
        else:
            while self.layerCount > count:
                self.layerCount -= 1
                i = self.layout.count()
                print("REMOVING", i)
                self.layout.takeAt(i)

    @property
    def layers(self):
        print(self.layout.findChildren(QtCore.QObject))
        return self.layout.findChildren(QtCore.QObject)

    ######## FEATURES ########

    @QtCore.pyqtSlot(int)
    def addLayer(self, pos: int):
        # TODO: use this function on initialization
        newLayer = LayerBar(pos, BLOCK_SIZE)
        self.layout.insertWidget(pos, newLayer)
        self.layerAdded.emit(pos)

    @QtCore.pyqtSlot(int)
    def removeLayer(self, pos: int):
        removedLayer = self.layers[id]
        self.layout.removeWidget(removedLayer)
        self.layerRemoved.emit(pos)

    def moveLayer(self, id, newPos):
        layer = self.layers[id]

        self.layout.removeWidget(layer)
        self.layout.insertWidget(newPos, layer)

        self.updateIds()
        self.layerMoved.emit(id, newPos)

    @QtCore.pyqtSlot(int)
    def shiftLayerUp(self, id):
        if id == 0:
            return
        self.moveLayer(id, id - 1)

    @QtCore.pyqtSlot(int)
    def shiftLayerDown(self, id):
        if id == len(self.layers) - 1:
            return
        self.moveLayer(id, id + 1)

    def updateIds(self):
        # TODO: change to signal and connect on layer creation
        for i, layer in enumerate(self.layers):
            layer.setId(i)
