import math
import os
from datetime import datetime, timedelta
from typing import List, Optional, Sequence, Tuple, Union

import numpy as np
from openal.audio import SoundData, SoundSink, SoundSource
from pydub import AudioSegment
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
        length_seconds = (
            len(sound.data) / 4 * (1 / pitch) / 44100
        )  # 4 = 2 channels * 2 bytes per sample
        self.end_time = datetime.now() + timedelta(seconds=length_seconds)
        # print(datetime.now(), self.end_time, length_seconds)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} ({len(self.sound.data)} samples)>"


class AudioSourcePool:
    def __init__(self, sources: int = 256) -> None:
        self.free_sources = [SoundSource() for _ in range(sources)]

    def get_source(self) -> SoundSource:
        if self.free_sources:
            # src = self.free_sources.pop()
            # print("SOURCE:", src.dataproperties)
            # print(len(self.free_sources))
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

        # self.sink.process_source(source)

        # print(source.dataproperties)

        sound = SoundInstance(samples, source, volume, pitch, panning)
        self.active_sounds.insert(0, sound)

        self.sink.play(source)
        # self.update()

    def update(self):
        # self.sink.update()
        # TODO: use a deque instead of a list / it might be possible
        # to avoid checking every single sound, if they're sorted by
        # end time
        for sound in self.active_sounds:
            # TODO: test polling the source state instead of using a timer
            # if sound.source["dataproperties"]["source_state"] == al.PLAYING:
            if datetime.now() >= sound.end_time:
                # print("STOPPING SOUND - ", datetime.now() - sound.end_time)
                self.active_sounds.remove(sound)
                self.sink.stop(sound.source)
                # self.sink.rewind(sound.source)
                self.source_pool.release_source(sound.source)
                sound.source.bufferqueue.clear()
                # self.sink.process_source(sound.source)
                # self.sink.refresh(sound.source)
        self.sink.update()


class AudioEngine(QtCore.QObject):
    soundLoaded = QtCore.pyqtSignal(int, bool)
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
        self.update_timer.timeout.connect(self.handler.update)
        self.update_timer.start()

    def run(self):
        # self.handler.start()
        pass

    def stop(self):
        print("Stopping audio engine")
        # self.handler.stop()
        # self.handler.close()
        self.finished.emit()

    @QtCore.pyqtSlot(str)
    def loadSound(self, path: PathLike) -> None:
        # TODO: use unique ID as sound identifier instead of index
        print("LOADING:", path)
        try:
            sound = AudioSegment.from_file(path)
        except (PermissionError, FileNotFoundError):
            self.sounds.append(None)
            print("LAST ID:", len(self.sounds) - 1)
            print("Failed to load sound")
            return
        sound = sound.set_frame_rate(self.sample_rate).set_sample_width(2)
        if sound.channels < self.channels:
            sound = AudioSegment.from_mono_audiosegments(*[sound] * self.channels)

        samples = np.array(sound.get_array_of_samples(), dtype="int16")
        samples = samples.astype(np.int16, order="C")
        samples = np.reshape(
            samples, (math.ceil(len(samples) / self.channels), self.channels), "C"
        )

        buf = samples.tobytes("C")
        channels = sound.channels
        bitrate = sound.sample_width * 8
        samplerate = sound.frame_rate

        data = SoundData(buf, channels, bitrate, len(buf), samplerate)
        # data = (buf, channels, bitrate, len(buf), samplerate)
        self.sounds.append(data)

        print(f"Loaded {path}")
        print("LAST ID:", len(self.sounds) - 1)
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
