from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class Layer:
    name: str = ""
    lock: bool = False
    solo: bool = False
    volume: int = 100
    panning: int = 0


@dataclass
class Instrument:
    name: str
    pitch: int = 45
    press: bool = False
    color: Optional[Tuple[int, int, int]] = None
    sound_path: Optional[str] = None
    icon_path: Optional[str] = None


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
class SongHeader:
    version: int
    default_instruments: int
    title: str = ""
    author: str = ""
    original_author: str = ""
    description: str = ""
    tempo: float = 10
    time_signature: int = 4
    minutes_spent: int = 0
    left_clicks: int = 0
    right_clicks: int = 0
    blocks_added: int = 0
    blocks_removed: int = 0
    song_origin: str = ""
    loop: bool = False
    max_loop_count: int = 0
    loop_start_tick: int = 0


@dataclass
class Song:
    header: SongHeader
    notes: list[Note]
    layers: list[Layer]
    instruments: list[Instrument]


default_instruments = [
    Instrument(
        name="Harp",
        sound_path="harp.ogg",
        icon_path="harp.png",
        color=(25, 100, 172),
        press=True,
    ),
    Instrument(
        name="Double Bass",
        sound_path="double_bass.ogg",
        icon_path="double_bass.png",
        color=(60, 142, 72),
        press=False,
    ),
    Instrument(
        name="Bass Drum",
        sound_path="bass_drum.ogg",
        icon_path="bass_drum.png",
        color=(190, 107, 107),
        press=False,
    ),
    Instrument(
        name="Snare Drum",
        sound_path="snare_drum.ogg",
        icon_path="snare_drum.png",
        color=(190, 190, 25),
        press=False,
    ),
    Instrument(
        name="Click",
        sound_path="click.ogg",
        icon_path="click.png",
        color=(157, 90, 152),
        press=True,
    ),
    Instrument(
        name="Guitar",
        sound_path="guitar.ogg",
        icon_path="guitar.png",
        color=(77, 60, 152),
        press=True,
    ),
    Instrument(
        name="Flute",
        sound_path="flute.ogg",
        icon_path="flute.png",
        color=(190, 182, 92),
        press=True,
    ),
    Instrument(
        name="Bell",
        sound_path="bell.ogg",
        icon_path="bell.png",
        color=(190, 25, 190),
        press=True,
    ),
    Instrument(
        name="Chime",
        sound_path="chime.ogg",
        icon_path="chime.png",
        color=(82, 142, 157),
        press=True,
    ),
    Instrument(
        name="Xylophone",
        sound_path="xylophone.ogg",
        icon_path="xylophone.png",
        color=(190, 190, 190),
        press=True,
    ),
    Instrument(
        name="Iron Xylophone",
        sound_path="iron_xylophone.ogg",
        icon_path="iron_xylophone.png",
        color=(25, 145, 190),
        press=True,
    ),
    Instrument(
        name="Cow Bell",
        sound_path="cow_bell.ogg",
        icon_path="cow_bell.png",
        color=(190, 35, 40),
        press=True,
    ),
    Instrument(
        name="Didgeridoo",
        sound_path="didgeridoo.ogg",
        icon_path="didgeridoo.png",
        color=(190, 87, 40),
        press=True,
    ),
    Instrument(
        name="Bit",
        sound_path="bit.ogg",
        icon_path="bit.png",
        color=(25, 190, 25),
        press=True,
    ),
    Instrument(
        name="Banjo",
        sound_path="banjo.ogg",
        icon_path="banjo.png",
        color=(190, 25, 87),
        press=True,
    ),
    Instrument(
        name="Pling",
        sound_path="pling.ogg",
        icon_path="pling.png",
        color=(87, 87, 87),
        press=True,
    ),
]
