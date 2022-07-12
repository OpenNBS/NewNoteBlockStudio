from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class Instrument:
    name: str
    color: Tuple[int, int, int]
    pitch: int = 45
    press: bool = False
    sound_path: Optional[str] = None
    icon_path: Optional[str] = None


default_instruments = [
    # fmt: off
    Instrument("Harp",           "harp.ogg",           "harp.png",           (25, 100, 172),  45, True),
    Instrument("Double Bass",    "double_bass.ogg",    "double_bass.png",    (60, 142, 72),   45, False),
    Instrument("Bass Drum",      "bass_drum.ogg",      "bass_drum.png",      (190, 107, 107), 45, False),
    Instrument("Snare Drum",     "snare_drum.ogg",     "snare_drum.png",     (190, 190, 25),  45, False),
    Instrument("Click",          "click.ogg",          "click.png",          (157, 90, 152),  45, True),
    Instrument("Guitar",         "guitar.ogg",         "guitar.png",         (77, 60, 152),   45, True),
    Instrument("Flute",          "flute.ogg",          "flute.png",          (190, 182, 92),  45, True),
    Instrument("Bell",           "bell.ogg",           "bell.png",           (190, 25, 190),  45, True),
    Instrument("Chime",          "chime.ogg",          "chime.png",          (82, 142, 157),  45, True),
    Instrument("Xylophone",      "xylophone.ogg",      "xylophone.png",      (190, 190, 190), 45, True),
    Instrument("Iron Xylophone", "iron_xylophone.ogg", "iron_xylophone.png", (25, 145, 190),  45, True),
    Instrument("Cow Bell",       "cow_bell.ogg",       "cow_bell.png",       (190, 35, 40),   45, True),
    Instrument("Didgeridoo",     "didgeridoo.ogg",     "didgeridoo.png",     (190, 87, 40),   45, True),
    Instrument("Bit",            "bit.ogg",            "bit.png",            (25, 190, 25),   45, True),
    Instrument("Banjo",          "banjo.ogg",          "banjo.png",          (190, 25, 87),   45, True),
    Instrument("Pling",          "pling.ogg",          "pling.png",          (87, 87, 87),    45, True),
    # fmt: on
]
