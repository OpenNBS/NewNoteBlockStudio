from typing import List, Optional, Sequence

from PyQt5 import QtCore

from nbs.core.data import Layer

EMPTY_LAYER = Layer()


class LayerController(QtCore.QObject):
    """Object that manages a sequence of layers."""

    visibleLayerCountChanged = QtCore.pyqtSignal(int)
    populatedLayerCountChanged = QtCore.pyqtSignal(int)
    layerAdded = QtCore.pyqtSignal(int, object)
    layerRemoved = QtCore.pyqtSignal(int)
    layerSwapped = QtCore.pyqtSignal(int, int)
    layerNameChanged = QtCore.pyqtSignal(int, str)
    layerVolumeChanged = QtCore.pyqtSignal(int, int)
    layerPanningChanged = QtCore.pyqtSignal(int, int)
    layerLockChanged = QtCore.pyqtSignal(int, bool)
    layerSoloChanged = QtCore.pyqtSignal(int, bool)

    def __init__(self, layers: List[Layer], parent: QtCore.QObject = None) -> None:
        super().__init__(parent)
        self.layers = layers
        self.workspaceLayerCount = 0

    def setWorkspaceLayerCount(self, count: int) -> None:
        """
        Set the number of layers visible on the note block area.
        This is used to ensure that at least these many layers
        are created, allowing the user to interact with them.
        """
        self.workspaceLayerCount = count
        print("LayerController.setWorkspaceLayerCount:", count)
        self.updateLayerCount()

    def updateLayerCount(self) -> None:
        """
        Create or delete enough layers to match the last populated layer
        in the song, be it in the note block area or in the layer list.
        """
        # This ensures that at least: a) the number of rows visible
        # on the note block area, and b) the last layer that has had
        # its data changed, whichever is bigger, have a layer object
        # associated with them. All extra layers are discarded.
        # This makes this object the "single source of truth" for
        # the number of layers in the song - the workspace can "request"
        # the addition of more layers through the setWorkspaceLayerCount()
        # slot, but this object will handle their creation.
        count = max(self.lastPopulatedLayerId, self.workspaceLayerCount)
        previousCount = len(self.layers)
        print("LayerController.updateLayerCount:", count)
        while len(self.layers) < count:
            print("Creating layer")
            self.layers.append(Layer())
        while len(self.layers) > count:
            print("Removing layer")
            self.layers.pop()
        if count != previousCount:
            self.visibleLayerCountChanged.emit(count)
            print(f"Layer count changed from {previousCount} to {count}")
        self.updatePopulatedLayerCount()
        # Visible = how many layers should appear on the screen (includes "fake" layers at the bottom)
        # Populated = how many layers have had their data changed

    @property
    def lastPopulatedLayerId(self) -> int:
        """
        Return the index of the last layer that has had its data changed.
        Used to ensure that at least this many layers remain visible.
        """
        for i in range(len(self.layers) - 1, -1, -1):
            if self.layers[i] != EMPTY_LAYER:
                return i
        return -1

    def updatePopulatedLayerCount(self) -> None:
        self.populatedLayerCountChanged.emit(self.lastPopulatedLayerId + 1)

    @QtCore.pyqtSlot(int, str)
    def loadLayers(self, layers: Sequence[Layer]) -> None:
        for i, layer in enumerate(layers):
            if i < len(self.layers):
                self.layers[i] = layer
                self.layerNameChanged.emit(i, layer.name)
                self.layerVolumeChanged.emit(i, layer.volume)
                self.layerPanningChanged.emit(i, layer.panning)
                self.layerLockChanged.emit(i, layer.lock)
                self.layerSoloChanged.emit(i, layer.solo)
            else:
                self.addLayer(layer=layer)

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
        self.updatePopulatedLayerCount()

    @QtCore.pyqtSlot(int)
    def removeLayer(self, id: int) -> None:
        self.layers.pop(id)
        self.layerRemoved.emit(id)
        self.updatePopulatedLayerCount()

    @QtCore.pyqtSlot(int, str)
    def setLayerName(self, id: int, name: str) -> None:
        self.layers[id].name = name
        self.layerNameChanged.emit(id, name)
        self.updatePopulatedLayerCount()

    @QtCore.pyqtSlot(int, int)
    def setLayerVolume(self, id: int, volume: int) -> None:
        self.layers[id].volume = volume
        self.layerVolumeChanged.emit(id, volume)
        self.updatePopulatedLayerCount()

    @QtCore.pyqtSlot(int, int)
    def setLayerPanning(self, id: int, panning: int) -> None:
        self.layers[id].panning = panning
        self.layerPanningChanged.emit(id, panning)
        self.updatePopulatedLayerCount()

    @QtCore.pyqtSlot(int, bool)
    def setLayerLock(self, id: int, lock: bool) -> None:
        self.layers[id].lock = lock
        self.layerLockChanged.emit(id, lock)
        self.updatePopulatedLayerCount()

    @QtCore.pyqtSlot(int, bool)
    def setLayerSolo(self, id: int, solo: bool) -> None:
        self.layers[id].solo = solo
        self.layerSoloChanged.emit(id, solo)
        self.updatePopulatedLayerCount()

    @QtCore.pyqtSlot(int, int)
    def swapLayers(self, id1: int, id2: int) -> None:
        self.layers[id1], self.layers[id2] = self.layers[id2], self.layers[id1]
        self.layerSwapped.emit(id1, id2)
        self.updatePopulatedLayerCount()
