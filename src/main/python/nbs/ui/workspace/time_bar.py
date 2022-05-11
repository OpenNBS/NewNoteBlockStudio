from PyQt5 import QtCore, QtGui, QtWidgets
from nbs.core.utils import *


__all__ = ["TimeBar"]


class SongTime(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tempo = 10
        self.currentTime = 10
        self.totalTime = 100

    def paintEvent(self, event):
        # TODO: this can probably be a QLabel
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setPen(QtCore.Qt.black)

        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        painter.setFont(font)

        height = self.height()
        midpoint = height / 2
        width = self.width()
        rect = QtCore.QRect(0, 0, width, midpoint)

        alignFlags = QtCore.Qt.AlignRight + QtCore.Qt.AlignTop

        painter.drawText(
            rect, alignFlags, ticks_to_timestr(self.currentTime, self.tempo)
        )

        font.setPointSize(8)
        font.setBold(False)
        rect.translate(0, midpoint)

        painter.setFont(font)
        painter.drawText(
            rect, alignFlags, f"/ {ticks_to_timestr(self.totalTime, self.tempo)}"
        )
        painter.end()

    @QtCore.pyqtSlot(float)
    def tempoChanged(self, newTempo: float):
        self.tempo = newTempo
        self.repaint()

    @QtCore.pyqtSlot(float)
    def currentTimeChanged(self, newTime: float):
        self.currentTime = newTime
        self.repaint()

    @QtCore.pyqtSlot(int)
    def totalTimeChanged(self, newTime: int):
        self.totalTime = newTime
        self.repaint()


class TempoBox(QtWidgets.QDoubleSpinBox):

    tempoChanged = QtCore.pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tempo = 10
        self.useBpm = False
        self.initUI()

    def initUI(self):
        self.setRange(0.1, 60)
        self.setSingleStep(0.25)
        self.setValue(self.tempo)
        self.setAlignment(QtCore.Qt.AlignRight)
        self.setSuffix(" t/s")
        self.valueChanged.connect(self.changeTempo)
        self.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)

    def contextMenuEvent(self, e: QtGui.QContextMenuEvent) -> None:
        # As there's no hook to modify the items on the default QSpinBox
        # context menu, we have to capture immediately as it appears. See:
        # https://stackoverflow.com/a/53504994/9045426

        QtCore.QTimer.singleShot(0, self.addContextMenuActions)
        return super().contextMenuEvent(e)

    def addContextMenuActions(self):
        for w in QtWidgets.QApplication.topLevelWidgets():
            if isinstance(w, QtWidgets.QMenu) and w.objectName() == "qt_edit_menu":
                w.clear()
                # w.addSeparator()
                setToTpsAction = w.addAction("t/s")
                setToBpmAction = w.addAction("BPM")
                setToTpsAction.triggered.connect(self.changeToTps)
                setToBpmAction.triggered.connect(self.changeToBpm)

                setToTpsAction.setCheckable(True)
                setToBpmAction.setCheckable(True)
                if not self.useBpm:
                    setToTpsAction.setChecked(True)
                else:
                    setToBpmAction.setChecked(True)

    @QtCore.pyqtSlot(float)
    def changeTempo(self, tempo: float):
        if self.useBpm:
            self.tempo = tempo / 15
        else:
            self.tempo = tempo
        self.tempoChanged.emit(self.tempo)

    @QtCore.pyqtSlot()
    def changeToTps(self):
        if self.useBpm:
            self.useBpm = False
            self.updateUnit()

    @QtCore.pyqtSlot()
    def changeToBpm(self):
        if not self.useBpm:
            self.useBpm = True
            self.updateUnit()

    def updateUnit(self):
        if self.useBpm:
            self.setSuffix(" BPM")
            self.setRange(1, 60 * 15)
            self.setValue(self.value() * 15)
            self.setSingleStep(1)
        else:
            self.setSuffix(" t/s")
            self.setValue(self.value() / 15)
            self.setRange(0.25, 60)
            self.setSingleStep(0.25)


class TimeBar(QtWidgets.QWidget):

    tempoChanged = QtCore.pyqtSignal(float)
    currentTimeChanged_ = QtCore.pyqtSignal(float)
    totalTimeChanged_ = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(32)
        self.currentTime = 0
        self.totalTime = 0
        self.tempo = 10.0
        self.displayBpm = False
        self.initUI()
        self.connectSignals()

    def initUI(self):
        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setMaximumWidth(342)  # TODO: calculate instead of hardcode

        # Song time
        self.songTime = SongTime()
        self.tempoBox = TempoBox()
        self.layout.addWidget(self.songTime)
        self.layout.addWidget(self.tempoBox)

        self.tempoBox.tempoChanged.connect(self.tempoChanged)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.tempoBox)
        layout.setContentsMargins(0, 0, 0, 0)
        container = QtWidgets.QWidget()
        container.setLayout(layout)

        self.layout.addWidget(self.songTime)
        self.layout.addWidget(container)

    def connectSignals(self):
        # Song time
        self.tempoChanged.connect(self.songTime.tempoChanged)
        self.currentTimeChanged_.connect(self.songTime.currentTimeChanged)
        self.totalTimeChanged_.connect(self.songTime.totalTimeChanged)

    def changeTempo(self):
        newValue = self.tempoBox.value()
        if self.displayBpm:
            self.tempo = newValue / 15
        else:
            self.tempo = newValue
        self.tempoChanged.emit(self.tempo)

    @QtCore.pyqtSlot(float)
    def currentTimeChanged(self, newPosInTicks: float):
        self.currentTime = newPosInTicks
        self.currentTimeChanged_.emit(self.currentTime)

    @QtCore.pyqtSlot(float)
    def songLengthChanged(self, newSongLength: float):
        self.totalTime = newSongLength
        self.totalTimeChanged_.emit(self.totalTime)
