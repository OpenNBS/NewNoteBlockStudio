import os
from dataclasses import dataclass
from typing import Union

import pynbs

PathLike = Union[str, bytes, os.PathLike]

CURRENT_NBS_VERSION = 5


@dataclass
class Instrument:
    id: int
    name: str
    file: str
    pitch: int = 45
    press_key: bool = True


@dataclass
class Note:
    tick: int
    layer: int
    instrument: int
    key: int
    velocity: int = 100
    panning: int = 0
    pitch: int = 0


@dataclass
class Layer:
    id: int
    name: str = ""
    lock: bool = False
    volume: int = 100
    panning: int = 0


class Song:
    def __init__(self, header, notes, layers=[], instruments=[]):
        self.header = header
        self.notes = notes
        self.layers = layers
        self.instruments = instruments

    @classmethod
    def from_file(cls, path: PathLike):
        song = pynbs.read(path)
        header = song.header
        notes = song.notes
        layers = song.layers
        instruments = song.instruments
        return cls(header, notes, layers, instruments)

    def save(self, path: PathLike, version: int = CURRENT_NBS_VERSION):
        file = pynbs.File(**self.header)
        file.notes.extend(self.notes)
        file.layers.extend(self.layers)
        file.instruments.extend(self.instruments)
        file.save(path, version=version)
