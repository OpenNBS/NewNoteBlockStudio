import os
import tempfile
from typing import Union

from pydub import AudioSegment
from PyQt5 import QtCore, QtMultimedia


class AudioEngine(QtMultimedia.QMediaPlayer):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.playlist = QtMultimedia.QMediaPlaylist()
        self.setPlaylist(self.playlist)

    def loadSound(self, path: Union[str, bytes, os.PathLike]):
        sound = AudioSegment.from_file(path)

        sound.export(path + "_temp.wav", format="wav")
        url = QtCore.QUrl.fromLocalFile(path + "_temp.wav")
        print(str(path))
        media = QtMultimedia.QMediaContent(url)
        self.playlist.addMedia(media)

        with tempfile.NamedTemporaryFile() as tmp:
            print(tmp.name)

    @QtCore.pyqtSlot(int, int, float, float)
    def play_sound(self, index: int, volume: int, pitch: float, panning: float):
        self.playlist.setCurrentIndex(index)

        self.setVolume(volume)
        self.setPlaybackRate(pitch)
        self.play()

        print(index, volume, pitch, "Sound played")
        # instantiate a QSoundEffect instead?
        # https://doc.qt.io/qt-5/qsoundeffect.html
        # https://doc.qt.io/qt-5/audiooverview.html
        # https://forum.qt.io/topic/7506/real-time-audio-processing-with-qt/5

    def changeOutputDevice(self):
        pass


class AudioMonitor(QtMultimedia.QAudioProbe):
    pass
