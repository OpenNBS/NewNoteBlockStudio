import math
import os
from dataclasses import dataclass
from typing import List, Union

import numpy as np
import sounddevice as sd
from pydub import AudioSegment
from PyQt5 import QtCore

PathLike = Union[str, bytes, os.PathLike]


def vol_to_gain(vol: float) -> float:
    return math.log(max(vol, 0.0001), 10) * 20


sd.default.samplerate = 44100
sd.default.blocksize = 0
sd.default.channels = 2
sd.default.dtype = "float32"
sd.default.latency = "low"


@dataclass
class SoundInstance:
    samples: np.ndarray
    current_frame: int = 0

    def __repr__(self):
        return f"<{self.__class__.__name__} ({self.current_frame}/{len(self.samples)})>"


class SoundQueue:
    def __init__(self, sample_rate, channels) -> None:
        self.active_sounds = []
        self.sample_rate = sample_rate
        self.channels = channels

    def push_sound(self, samples: np.ndarray) -> None:
        sound = SoundInstance(samples)
        self.active_sounds.append(sound)

    def get_active_sounds(self) -> List[SoundInstance]:
        for sound in self.active_sounds:
            if sound.current_frame >= len(sound.samples):
                self.active_sounds.remove(sound)
        return self.active_sounds


class AudioOutputHandler:
    def __init__(self, sample_rate, channels) -> None:
        self.sample_rate = sample_rate
        self.channels = channels
        self.queue = SoundQueue(sample_rate, channels)
        self.stream = sd.OutputStream(callback=lambda *args: self.callback(*args))

    def push_samples(self, samples: np.ndarray) -> None:
        self.queue.push_sound(samples)

    def start(self) -> None:
        self.stream.start()

    def stop(self) -> None:
        self.stream.stop()

    def close(self) -> None:
        self.stream.close()

    def __enter__(self) -> None:
        self.start()
        return self

    def __exit__(self, *args) -> None:
        self.stop()
        self.close()

    def callback(self, outdata: np.ndarray, frames: int, time, status) -> None:
        if status:
            print(status)
        sounds = self.queue.get_active_sounds()
        outdata.fill(0)
        for sound in sounds:
            start = sound.current_frame
            length = sound.samples.shape[0]
            end = min(start + frames, length)

            # print("Current:", sound.current_frame, start + frames, length, end)

            samples = sound.samples[start:end]
            if samples.shape[0] == 0:
                print("AUDIO: No samples left")
                continue
            outdata[: end - start] += samples
            sound.current_frame += frames


class AudioEngine(QtCore.QObject):
    def __init__(self, parent=None, sample_rate=44100, channels=2):
        super().__init__(parent)
        self.sample_rate = sample_rate
        self.channels = channels
        self.sounds = []

        self.handler = AudioOutputHandler(sample_rate, channels)
        self.handler.start()

    def loadSound(self, path: PathLike):
        sound = AudioSegment.from_file(path)

        sound = sound.set_frame_rate(self.sample_rate).set_sample_width(2)

        if sound.channels < self.channels:
            sound = AudioSegment.from_mono_audiosegments(*[sound] * self.channels)

        self.sounds.append(sound)

    @QtCore.pyqtSlot(int, float, float, float)
    def playSound(self, index: int, volume: float, pitch: float, panning: float):

        sound = self.sounds[index]

        new_sound = (
            sound._spawn(
                sound.raw_data,
                overrides={"frame_rate": round(sound.frame_rate * pitch)},
            )
            .set_frame_rate(sound.frame_rate)
            .apply_gain(vol_to_gain(volume))
            .pan(panning)
        )

        samples = np.array(new_sound.get_array_of_samples(), dtype="int16")
        samples = samples.astype(np.float32, order="C") / 32768.0
        samples = np.reshape(
            samples, (math.ceil(len(samples) / self.channels), self.channels), "C"
        )
        self.handler.push_samples(samples)

        print(index, volume, pitch, "Sound played")
