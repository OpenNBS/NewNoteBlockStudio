from typing import List, Optional, Sequence

import qtawesome as qta
from nbs.core.data import Layer
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

    nameChanged = QtCore.pyqtSignal(int, str)
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
        self.setFixedHeight(height)

        self.toolbar = QtWidgets.QToolBar()
        self.toolbar.setIconSize(QtCore.QSize(16, 24))
        self.toolbar.setFixedHeight(height)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(5, 0, 5, 0)
        layout.addWidget(self.toolbar)
        self.setLayout(layout)

        self.nameBox = QtWidgets.QLineEdit()
        self.nameBox.setFixedSize(76, 16)
        self.nameBox.setPlaceholderText("Layer {}".format(self.id + 1))
        self.nameBox.setText(self.name)
        self.nameBox.textChanged.connect(
            lambda value: self.nameChanged.emit(self.id, value)
        )
        self.toolbar.addWidget(self.nameBox)

        self.volumeDial = QtWidgets.QDial()
        self.volumeDial.setNotchesVisible(True)
        self.volumeDial.setNotchTarget(3.5)
        self.volumeDial.setSingleStep(10)
        self.volumeDial.setRange(0, 100)
        self.volumeDial.setValue(100)
        self.volumeDial.setNotchesVisible(True)
        self.volumeDial.setContentsMargins(0, 0, 0, 0)
        self.volumeDial.setMaximumWidth(32)
        self.toolbar.addWidget(self.volumeDial)

        self.panningDial = QtWidgets.QDial()
        self.panningDial.setNotchesVisible(True)
        self.panningDial.setNotchTarget(3.5)
        self.panningDial.setSingleStep(10)
        self.panningDial.setRange(-100, 100)
        self.panningDial.setValue(0)
        self.panningDial.setContentsMargins(0, 0, 0, 0)
        self.panningDial.setMaximumWidth(32)
        self.toolbar.addWidget(self.panningDial)

        # self.addAction(self.icons["volume"], "Volume")
        # self.addAction(self.icons["stereo"], "Stereo panning")
        lockAction = self.toolbar.addAction(self.icons["lock"], "Lock this layer")
        lockAction.setCheckable(True)
        lockAction.triggered.connect(
            lambda checked: self.lockChanged.emit(self.id, checked)
        )

        soloAction = self.toolbar.addAction(
            self.icons["solo"],
            "Solo this layer",
        )
        soloAction.setCheckable(True)
        soloAction.triggered.connect(
            lambda checked: self.lockChanged.emit(self.id, checked)
        )

        selectAllAction = self.toolbar.addAction(
            self.icons["select_all"],
            "Select all note blocks in this layer",
            lambda: self.selectAllClicked.emit(self.id),
        )
        addAction = self.toolbar.addAction(
            self.icons["insert"],
            "Add empty layer here",
            lambda: self.addClicked.emit(self.id),
        )
        removeAction = self.toolbar.addAction(
            self.icons["remove"],
            "Remove this layer",
            lambda: self.removeClicked.emit(self.id),
        )
        shiftUpAction = self.toolbar.addAction(
            self.icons["shift_up"],
            "Shift layer up",
            lambda: self.shiftUpClicked.emit(self.id),
        )
        shiftDownAction = self.toolbar.addAction(
            self.icons["shift_down"],
            "Shift layer down",
            lambda: self.shiftDownClicked.emit(self.id),
        )

    @QtCore.pyqtSlot(float)
    def changeScale(self, newHeight):
        self.setFixedHeight(newHeight)
        self.toolbar.setFixedHeight(newHeight)
        if newHeight < BLOCK_SIZE // 2:
            self.toolbar.hide()
        else:
            self.toolbar.show()

    def setId(self, newId: int):
        self.id = newId
        self.nameBox.setPlaceholderText("Layer {}".format(self.id + 1))

    def setName(self, name: str):
        self.name = name
        self.nameBox.setText(name)

    def setVolume(self, volume: int):
        self.volume = volume
        self.volumeDial.setValue(volume)

    def setPanning(self, panning: int):
        self.panning = panning
        self.panningDial.setValue(panning)

    def setLocked(self, locked: bool):
        self.locked = locked
        self.toolbar.actions()[0].setChecked(locked)

    def setSolo(self, solo: bool):
        self.solo = solo
        self.toolbar.actions()[1].setChecked(solo)

    # def setSelected(self, selected: bool):
    #    self.selected = selected
    #    self.setFrameShadow(QtWidgets.QFrame.Raised if selected else QtWidgets.QFrame.Plain)


class LayerArea(VerticalScrollArea):

    layerNameChangeRequested = QtCore.pyqtSignal(int, str)
    layerVolumeChangeRequested = QtCore.pyqtSignal(int, int)
    layerPanningChangeRequested = QtCore.pyqtSignal(int, int)
    layerLockChangeRequested = QtCore.pyqtSignal(int, bool)
    layerSoloChangeRequested = QtCore.pyqtSignal(int, bool)
    layerSelectRequested = QtCore.pyqtSignal(int)
    layerAddRequested = QtCore.pyqtSignal(int)
    layerRemoveRequested = QtCore.pyqtSignal(int)
    layerMoveRequested = QtCore.pyqtSignal(int, int)

    scaleChanged = QtCore.pyqtSignal(float)

    def __init__(self, layerCount=200, parent=None):
        # TODO: do we need a default layer number? Should it be 200?
        super().__init__(parent)
        self.layerHeight = BLOCK_SIZE
        self.initUI(layerCount)

    def initUI(self, layerCount):
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(5, 0, 0, 0)
        self.container = QtWidgets.QWidget()
        self.container.setLayout(self.layout)
        self.container.setContentsMargins(0, 0, 0, 0)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setMaximumWidth(324)  # TODO: calculate instead of hardcode
        self.setWidget(self.container)

    def wheelEvent(self, event):
        # Prevent scrolling with the mouse wheel
        if event.type() == QtCore.QEvent.Wheel:
            event.ignore()

    @QtCore.pyqtSlot(float)
    def updateLayerHeight(self, newHeight):
        self.layerHeight = newHeight
        self.scaleChanged.emit(newHeight)

    @property
    def layers(self):
        layers = []
        for i in range(self.layout.count()):
            layers.append(self.layout.itemAt(i).widget())
        return layers

    @property
    def layerCount(self):
        return self.layout.count()

    def createLayer(self, pos: int, layer: Layer):
        """
        Create a new `LayerBar` widget for the corresponding `layer` at the given `pos`,
        and add it to the layout.
        """
        pos = pos if pos is not None else self.layerCount
        args = (
            layer.name,
            layer.volume,
            layer.panning,
            layer.lock,
            layer.solo,
        )
        layerBar = LayerBar(pos, self.layerHeight, *args, parent=self)
        self.layout.insertWidget(pos, layerBar)

        self.scaleChanged.connect(layerBar.changeScale)
        layerBar.nameChanged.connect(self.layerNameChangeRequested)
        layerBar.volumeChanged.connect(self.layerVolumeChangeRequested)
        layerBar.panningChanged.connect(self.layerPanningChangeRequested)
        layerBar.lockChanged.connect(self.layerLockChangeRequested)
        layerBar.soloChanged.connect(self.layerSoloChangeRequested)
        layerBar.selectAllClicked.connect(self.layerSelectRequested)
        layerBar.addClicked.connect(self.layerAddRequested)
        layerBar.removeClicked.connect(self.layerRemoveRequested)
        layerBar.shiftUpClicked.connect(lambda *a: self.layerMoveRequested.emit(*a, -1))
        layerBar.shiftDownClicked.connect(
            lambda *a: self.layerMoveRequested.emit(*a, +1)
        )

    def deleteLayer(self, pos: int):
        """
        Delete the layer at position `pos` from the layout.
        """
        removedLayer = self.layout.takeAt(pos).widget()
        self.layout.removeWidget(removedLayer)
        removedLayer.deleteLater()

    def updateLayerIds(self):
        # Would've been better as a signal connected to all layers,
        # but we couldn't easily pass their ID to each one
        for i, layer in enumerate(self.layers):
            layer.setId(i)

    ####### SONG ########

    def getLayerData(self) -> List[Layer]:
        layers = []
        for layer in self.layers:
            layers.append(Layer())
        return layers

    ######## FEATURES ########

    @QtCore.pyqtSlot(int, Layer)
    def addLayer(self, pos: int, layer: Layer):
        self.createLayer(pos, layer)
        self.updateLayerIds()

    @QtCore.pyqtSlot(int)
    def removeLayer(self, id: int):
        self.deleteLayer(id)
        self.updateLayerIds()

    def moveLayer(self, id, newPos):
        layer = self.layers[id]
        self.layout.removeWidget(layer)
        self.layout.insertWidget(newPos, layer)
        self.updateLayerIds()

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

    @QtCore.pyqtSlot(int, str)
    def changeLayerName(self, id, name):
        self.layers[id].setName(name)

    @QtCore.pyqtSlot(int, int)
    def changeLayerVolume(self, id, volume):
        self.layers[id].setVolume(volume)

    @QtCore.pyqtSlot(int, int)
    def changeLayerPanning(self, id, panning):
        self.layers[id].setPanning(panning)

    @QtCore.pyqtSlot(int, bool)
    def changeLayerLock(self, id, lock):
        self.layers[id].setLock(lock)

    @QtCore.pyqtSlot(int, bool)
    def changeLayerSolo(self, id, solo):
        self.layers[id].setSolo(solo)
