import time

from PyQt5 import QtCore


class PlaybackController(QtCore.QObject):

    playbackPositionChanged = QtCore.pyqtSignal(float)

    def __init__(self, parent: QtCore.QObject = None):
        super().__init__(parent)
        self.tempo = 10.00
        self.currentTick = 0
        self.lastTickTimestamp = None

        self.timer = QtCore.QTimer()
        self.timer.setTimerType(QtCore.Qt.TimerType.PreciseTimer)
        self.timer.setInterval(1000 / 60)
        self.timer.timeout.connect(
            self.tickPlayback, QtCore.Qt.ConnectionType.DirectConnection
        )

    @QtCore.pyqtSlot()
    def play(self):
        self.lastTickTimestamp = None
        self.timer.start()

    @QtCore.pyqtSlot()
    def pause(self):
        self.timer.stop()

    @QtCore.pyqtSlot()
    def stop(self):
        self.timer.stop()
        self.currentTick = 0
        self.playbackPositionChanged.emit(self.currentTick)

    @QtCore.pyqtSlot(bool)
    def setPlaying(self, playing: bool) -> None:
        if playing:
            self.play()
        else:
            self.pause()

    @QtCore.pyqtSlot(float)
    def setPlaybackPosition(self, tick: float):
        self.currentTick = max(0, tick)
        self.playbackPositionChanged.emit(self.currentTick)

    @QtCore.pyqtSlot()
    def tickPlayback(self):
        offset = self.tempo / 60
        currentTimeMs = time.time_ns() / 10**6

        # Lag compensation
        if self.lastTickTimestamp is not None:
            timeDelta = currentTimeMs - self.lastTickTimestamp
            tickCompensationFactor = timeDelta / (1000 / 60)
            offset *= tickCompensationFactor

        self.lastTickTimestamp = currentTimeMs

        self.currentTick += offset
        self.playbackPositionChanged.emit(self.currentTick)

    @QtCore.pyqtSlot(float)
    def setTempo(self, tempo: float):
        self.tempo = tempo
