import math
import os
from typing import List, Sequence, Tuple, Union

import numpy as np
import samplerate as sr
import sounddevice as sd
from pydub import AudioSegment
from PyQt5 import QtCore

PathLike = Union[str, bytes, os.PathLike]


def key_to_pitch(key):
    return 2 ** (key / 12)


def vol_to_gain(vol: float) -> float:
    if vol == 0:
        return -float("inf")
    return math.log(vol, 10) * 20


def gain_to_vol(gain: float) -> float:
    return 10 ** (gain / 20)


sd.default.samplerate = 44100
sd.default.blocksize = 0
sd.default.channels = 2
sd.default.dtype = "float32"
sd.default.latency = "low"


def get_system_audio_devices():
    return sd.query_devices()


def query_device_info(id):
    return sd.query_devices(id)


def query_all_devices():
    return [
        query_device_info(device_id) for device_id in range(len(sd.query_devices()))
    ]


def query_default_output_device():
    input_device_id, output_device_id = sd.default.device
    return sd.query_devices(output_device_id)


def apply_volume(samples: np.ndarray, volume: float):
    samples *= volume


def apply_gain_stereo(samples: np.ndarray, left_gain: float, right_gain: float) -> None:
    l_mult_factor = gain_to_vol(left_gain)
    r_mult_factor = gain_to_vol(right_gain)

    samples[:, 0] *= l_mult_factor
    samples[:, 1] *= r_mult_factor


def apply_pan(samples: np.ndarray, pan: float) -> None:

    # Simplified panning algorithm from pydub to operate on numpy arrays
    # https://github.com/jiaaro/pydub/blob/0c26b10619ee6e31c2b0ae26a8e99f461f694e5f/pydub/effects.py#L284

    max_boost_db = vol_to_gain(2.0)
    boost_db = abs(pan) * max_boost_db

    boost_factor = gain_to_vol(boost_db)
    reduce_factor = gain_to_vol(max_boost_db) - boost_factor

    reduce_db = vol_to_gain(reduce_factor)
    boost_db /= 2.0

    if pan < 0:
        apply_gain_stereo(samples, boost_db, reduce_db)
    else:
        apply_gain_stereo(samples, reduce_db, boost_db)


class SoundInstance:
    def __init__(
        self,
        samples: np.ndarray,
        volume: float = 1.0,
        pitch: float = 1.0,
        pan: float = 0.0,
    ):
        self.samples = samples
        self.current_frame = 0

        self.volume = volume
        self.pitch = pitch
        self.pan = pan

        self.resampler = sr.CallbackResampler(
            callback=self.get_input_callback(), ratio=1 / self.pitch, channels=2
        )
        self.resampler.__enter__()

    def __repr__(self):
        return f"<{self.__class__.__name__} ({self.current_frame}/{len(self.samples)})>"

    def __del__(self):
        self.resampler.__exit__()

    def get_input_callback(self, n_frames: int = 256):
        def producer():
            while True:
                yield self.samples[self.current_frame : self.current_frame + n_frames]
                self.current_frame += n_frames

        return lambda p=producer(): next(p)

    def get_samples(self, n_frames: int):
        samples = self.resampler.read(n_frames)
        apply_volume(samples, self.volume)
        apply_pan(samples, self.pan)
        return samples


class SoundQueue:
    def __init__(self, sample_rate, channels) -> None:
        self.active_sounds = []
        self.sample_rate = sample_rate
        self.channels = channels

    def push_sound(
        self, samples: np.ndarray, pitch: float, volume: float, panning: float
    ) -> None:
        sound = SoundInstance(samples, volume, pitch, panning)
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
        self.stream = sd.OutputStream(
            callback=lambda *args: self.playback_callback(*args)
        )

    def push_sound(self, samples: np.ndarray, pitch, volume, panning) -> None:
        self.queue.push_sound(samples, pitch, volume, panning)

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

    def playback_callback(self, outdata: np.ndarray, frames: int, time, status) -> None:
        if status:
            print(status)

        outdata.fill(0)
        for sound in self.queue.get_active_sounds():
            samples = sound.get_samples(frames)
            end = len(samples)
            outdata[:end] += samples


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

        samples = np.array(sound.get_array_of_samples(), dtype="int16")
        samples = samples.astype(np.float32, order="C") / 32768.0
        samples = np.reshape(
            samples, (math.ceil(len(samples) / self.channels), self.channels), "C"
        )
        self.sounds.append(samples)

    @QtCore.pyqtSlot(int, float, float, float)
    def playSound(self, index: int, volume: float, key: float, panning: float):
        samples = self.sounds[index]
        pitch = key_to_pitch(key)

        self.handler.push_sound(samples, pitch, volume, panning)

        print(index, volume, pitch, "Sound played")

    def playSounds(self, sounds: Sequence[Tuple[int, float, float, float]]):
        for sound in sounds:
            self.playSound(*sound)
