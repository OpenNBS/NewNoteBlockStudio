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

    def __init__(
        self,
        num,
        height,
        name="",
        volume=100,
        panning=100,
        locked=False,
        solo=False,
        parent=None,
    ):
        super().__init__(parent)
        self.num = num
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
            "lock_locked": qta.icon("mdi.lock-outline"),
            "lock_unlocked": qta.icon("mdi.lock-open-variant-outline"),
            "solo": qta.icon("mdi.exclamation-thick"),
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
        self.nameBox.setPlaceholderText("Layer {}".format(self.num + 1))
        self.addWidget(self.nameBox)
        self.addAction(self.icons["volume"], "Volume")
        self.addAction(self.icons["stereo"], "Stereo panning")
        self.addAction(self.icons["lock_unlocked"], "Lock this layer")
        self.addAction(self.icons["solo"], "Solo this layer")
        self.addAction(self.icons["select_all"], "Select all note blocks in this layer")
        self.addAction(self.icons["insert"], "Add empty layer here")
        self.addAction(self.icons["remove"], "Remove this layer")
        self.addAction(self.icons["shift_up"], "Shift layer up")
        self.addAction(self.icons["shift_down"], "Shift layer down")

    @QtCore.pyqtSlot(float)
    def changeScale(self, factor):
        self.setFixedHeight(factor * BLOCK_SIZE - 2)
        if factor < 0.5:
            self.hide()
        else:
            self.show()


class LayerArea(VerticalScrollArea):

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
    def updateLayerCount(self, width, newSize):
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
