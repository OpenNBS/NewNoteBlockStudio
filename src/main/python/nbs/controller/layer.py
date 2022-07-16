from typing import Optional, Sequence

from nbs.core.data import Layer
from PyQt5 import QtCore


class LayerController(QtCore.QObject):
    """Object that manages a sequence of layers."""

    layerAdded = QtCore.pyqtSignal(int, Layer)
    layerRemoved = QtCore.pyqtSignal(int)
    layerMoved = QtCore.pyqtSignal(int, int)
    layerNameChanged = QtCore.pyqtSignal(int, str)
    layerVolumeChanged = QtCore.pyqtSignal(int, int)
    layerPanningChanged = QtCore.pyqtSignal(int, int)
    layerLockChanged = QtCore.pyqtSignal(int, bool)
    layerSoloChanged = QtCore.pyqtSignal(int, bool)

    def __init__(self, layers: Sequence[Layer], parent: QtCore.QObject = None) -> None:
        super().__init__(parent)
        self.layers = layers

    @QtCore.pyqtSlot(int)
    def updateLayerCount(self, count: int) -> None:

        # TODO: This is dangerous, because it creates the possibility of managing layers
        # SEPARATELY from the note block scene. We can never have less layers than
        # the note block scene, and the workspace should probably ensure this is not the case
        #
        # The workspace should do the internal syncing between the two, and have
        # methods to announce changes to the synced state, so that we don't need
        # to worry about it here.
        #
        # The problem is that the layer count is a shared state between layers and
        # note blocks - it's not a property of the layer controller, but of the workspace.
        # Since note blocks are managed by the NoteBlockArea, we need information there
        # in order to know how many layers there should exist.
        #
        # I don't think the main window should be responsible for managing this --
        # it's supposed to work at a higher level than that.

        print("LayerController.updateLayerCount:", count)

        while len(self.layers) < count:
            print("Adding layer")
            self.addLayer()
        # TODO: we might want to keep the layers there when "shrinking" the layer count to avoid data deletion?
        while len(self.layers) > count:
            self.layers.pop()
        print("New layer count:", len(self.layers))

    @QtCore.pyqtSlot()
    @QtCore.pyqtSlot(int)
    @QtCore.pyqtSlot(int, Layer)
    def addLayer(
        self, index: Optional[int] = None, layer: Optional[Layer] = None
    ) -> None:
        if index is None:
            index = len(self.layers)
        if layer is None:
            layer = Layer()
        self.layers.insert(index, layer)
        self.layerAdded.emit(index, layer)

    @QtCore.pyqtSlot(int)
    def removeLayer(self, id: int) -> None:
        self.layers.pop(id)
        self.layerRemoved.emit(self.layers[id])

    @QtCore.pyqtSlot(int, int)
    def setLayerName(self, id: int, name: str) -> None:
        self.layers[id].name = name
        self.layerNameChanged.emit(id, name)

    @QtCore.pyqtSlot(int, int)
    def setLayerVolume(self, id: int, volume: int) -> None:
        self.layers[id].volume = volume
        self.layerVolumeChanged.emit(id, volume)

    @QtCore.pyqtSlot(int, int)
    def setLayerPanning(self, id: int, panning: int) -> None:
        self.layers[id].panning = panning
        self.layerPanningChanged.emit(id, panning)

    @QtCore.pyqtSlot(int, bool)
    def setLayerLock(self, id: int, lock: bool) -> None:
        self.layers[id].lock = lock
        self.layerLockChanged.emit(id, lock)

    @QtCore.pyqtSlot(int, bool)
    def setLayerSolo(self, id: int, solo: bool) -> None:
        self.layers[id].solo = solo
        self.layerSoloChanged.emit(id, solo)

    @QtCore.pyqtSlot(int, int)
    def moveLayer(self, id: int, offset: int) -> None:
        self.swapLayers(id, id + offset)

    @QtCore.pyqtSlot(int, int)
    def swapLayers(self, id1: int, id2: int) -> None:
        self.layers[id1], self.layers[id2] = self.layers[id2], self.layers[id1]
        self.layerMoved.emit(id1, id2 - id1)
