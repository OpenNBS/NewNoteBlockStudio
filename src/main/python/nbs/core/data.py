from dataclasses import dataclass


@dataclass
class Instrument:
    name: str
    sound_path: str
    icon_path: str
    color: tuple[int, int, int]
    press: bool


default_instruments = [
    # fmt: off
    Instrument("Harp",           "harp.ogg",           "harp.png",           (25, 100, 172),  True),
    Instrument("Double Bass",    "double_bass.ogg",    "double_bass.png",    (60, 142, 72),   False),
    Instrument("Bass Drum",      "bass_drum.ogg",      "bass_drum.png",      (190, 107, 107), False),
    Instrument("Snare Drum",     "snare_drum.ogg",     "snare_drum.png",     (190, 190, 25),  False),
    Instrument("Click",          "click.ogg",          "click.png",          (157, 90, 152),  False),
    Instrument("Guitar",         "guitar.ogg",         "guitar.png",         (77, 60, 152),   False),
    Instrument("Flute",          "flute.ogg",          "flute.png",          (190, 182, 92),  False),
    Instrument("Bell",           "bell.ogg",           "bell.png",           (190, 25, 190),  False),
    Instrument("Chime",          "chime.ogg",          "chime.png",          (82, 142, 157),  False),
    Instrument("Xylophone",      "xylophone.ogg",      "xylophone.png",      (190, 190, 190), False),
    Instrument("Iron Xylophone", "iron_xylophone.ogg", "iron_xylophone.png", (25, 145, 190),  False),
    Instrument("Cow Bell",       "cow_bell.ogg",       "cow_bell.png",       (190, 35, 40),   False),
    Instrument("Didgeridoo",     "didgeridoo.ogg",     "didgeridoo.png",     (190, 87, 40),   False),
    Instrument("Bit",            "bit.ogg",            "bit.png",            (25, 190, 25),   False),
    Instrument("Banjo",          "banjo.ogg",          "banjo.png",          (190, 25, 87),   False),
    Instrument("Pling",          "pling.ogg",          "pling.png",          (87, 87, 87),    False),
    # fmt: on
]
