from dataclasses import dataclass


@dataclass
class Instrument:
    name: str
    sound_path: str
    icon_path: str
    press: bool


default_instruments = [
    # fmt: off
    Instrument("Harp",           "harp.ogg",           "harp.png",           True),
    Instrument("Double Bass",    "double_bass.ogg",    "double_bass.png",    False),
    Instrument("Bass Drum",      "bass_drum.ogg",      "bass_drum.png",      False),
    Instrument("Snare Drum",     "snare_drum.ogg",     "snare_drum.png",     False),
    Instrument("Click",          "click.ogg",          "click.png",          False),
    Instrument("Guitar",         "guitar.ogg",         "guitar.png",         False),
    Instrument("Flute",          "flute.ogg",          "flute.png",          False),
    Instrument("Bell",           "bell.ogg",           "bell.png",           False),
    Instrument("Chime",          "chime.ogg",          "chime.png",          False),
    Instrument("Xylophone",      "xylophone.ogg",      "xylophone.png",      False),
    Instrument("Iron Xylophone", "iron_xylophone.ogg", "iron_xylophone.png", False),
    Instrument("Cow Bell",       "cow_bell.ogg",       "cow_bell.png",       False),
    Instrument("Didgeridoo",     "didgeridoo.ogg",     "didgeridoo.png",     False),
    Instrument("Bit",            "bit.ogg",            "bit.png",            False),
    Instrument("Banjo",          "banjo.ogg",          "banjo.png",          False),
    Instrument("Pling",          "pling.ogg",          "pling.png",          False)
    # fmt: on
]
