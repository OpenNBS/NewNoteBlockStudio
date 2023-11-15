import math
from datetime import datetime, timedelta
from typing import List, Optional, Sequence, Tuple

import numpy as np
import soundfile as sf
from openal.audio import SoundData, SoundSink, SoundSource
from PyQt5 import QtCore

from nbs.utils.file import PathLike


def key_to_pitch(key: float) -> float:
    return 2 ** (key / 12)


class NoSourceAvailableException(Exception):
    pass


class SoundInstance:
    def __init__(
        self,
        sound: SoundData,
        source: SoundSource,
        volume: float = 1.0,
        pitch: float = 1.0,
        pan: float = 0.0,
    ) -> None:
        self.sound = sound
        self.source = source
        self.volume = volume
        self.pitch = pitch
        self.pan = pan
        sample_size = sound.channels * sound.bitrate // 8
        sample_rate = sound.frequency
        length_samples = sound.size * (1 / pitch)
        length_seconds = length_samples / (sample_size * sample_rate)
        self.end_time = datetime.now() + timedelta(seconds=length_seconds)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} ({len(self.sound.data)} samples)>"


class AudioSourcePool:
    def __init__(self, sources: int = 256) -> None:
        self.free_sources = [SoundSource() for _ in range(sources)]

    def get_source(self) -> SoundSource:
        if self.free_sources:
            return self.free_sources.pop()
        else:
            raise NoSourceAvailableException("No free audio sources available")

    def release_source(self, source: SoundSource) -> None:
        self.free_sources.append(source)


class AudioOutputHandler:
    def __init__(self):
        self.active_sounds: List[SoundInstance] = []
        self.source_pool = AudioSourcePool()
        self.sink = SoundSink()
        self.sink.activate()

    def push_sound(
        self, samples: SoundData, pitch: float, volume: float, panning: float
    ) -> None:
        try:
            source = self.source_pool.get_source()
        except NoSourceAvailableException:
            # TODO: remove oldest sound from active_sounds and use that source
            print("Skipping sound, no free sources available")
            return

        source.gain = volume
        source.pitch = pitch
        source.position = [panning, 0, 0]
        source.looping = False
        source.queue(samples)

        sound = SoundInstance(samples, source, volume, pitch, panning)
        self.active_sounds.insert(0, sound)

        self.sink.play(source)

    def update(self):
        # TODO: use a deque instead of a list / it might be possible
        # to avoid checking every single sound, if they're sorted by
        # end time
        for sound in self.active_sounds:
            # TODO: test polling the source state instead of using a timer
            # if sound.source["dataproperties"]["source_state"] == al.PLAYING:
            if datetime.now() >= sound.end_time:
                self.active_sounds.remove(sound)
                self.sink.stop(sound.source)
                self.source_pool.release_source(sound.source)
                sound.source.bufferqueue.clear()
        self.sink.update()


class AudioEngine(QtCore.QObject):
    soundLoaded = QtCore.pyqtSignal(int, bool)
    soundCountUpdated = QtCore.pyqtSignal(int)
    finished = QtCore.pyqtSignal()

    def __init__(
        self,
        parent: Optional[QtCore.QObject] = None,
        sample_rate: int = 44100,
        channels: int = 2,
    ):
        super().__init__(parent)
        self.sample_rate = sample_rate
        self.channels = channels
        self.master_volume = 0.5
        self.sounds = []
        self.handler = AudioOutputHandler()

        # Set up update timer
        self.update_timer = QtCore.QTimer()
        self.update_timer.setTimerType(QtCore.Qt.TimerType.PreciseTimer)
        self.update_timer.setInterval(16)
        self.update_timer.timeout.connect(self._update)
        self.update_timer.start()

    def run(self):
        pass

    def stop(self):
        print("Stopping audio engine")
        self.finished.emit()

    @QtCore.pyqtSlot(str)
    def loadSound(self, path: PathLike) -> None:
        # TODO: use unique ID as sound identifier instead of index
        print("LOADING:", path)
        try:
            samples, samplerate = sf.read(path, dtype="int16", always_2d=True)
        except sf.LibsndfileError:
            self.sounds.append(None)
            print("Failed to load sound")
            return
        buf = samples.tobytes("C")
        channels = samples.shape[1]
        bitrate = samples.dtype.itemsize * 8

        print(channels, bitrate, len(buf), samplerate)
        data = SoundData(buf, channels, bitrate, len(buf), samplerate)
        self.sounds.append(data)

        print(f"Loaded {path}")
        self.soundLoaded.emit(len(self.sounds) - 1, True)

    @QtCore.pyqtSlot(int)
    def removeSound(self, index: int) -> None:
        del self.sounds[index]

    @QtCore.pyqtSlot(int, float, float, float)
    def playSound(self, index: int, volume: float, key: float, panning: float):
        sound = self.sounds[index]
        if sound is None:
            return
        # data = SoundData(*sound)
        pitch = key_to_pitch(key)
        volume *= self.master_volume
        self.handler.push_sound(sound, pitch, volume, panning)

    @QtCore.pyqtSlot(list)
    def playSounds(self, sounds: Sequence[Tuple[int, float, float, float]]):
        for sound in sounds:
            self.playSound(*sound)

    @QtCore.pyqtSlot()
    def _update(self):
        self.handler.update()
        self.soundCountUpdated.emit(len(self.handler.active_sounds))
