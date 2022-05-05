import pynbs


def load_nbs(filename):
    """Loads a .nbs file from disk.
    Note: this package is updated for version 4 of the .nbs format, it does not currently work.
    Note: this could be extended to support multiprocessing to make loading faster.
    """
    song = pynbs.read(filename)
    header = song.header
    notes = song.notes
    layers = song.layers
    instruments = song.instruments
    return header, notes, layers, instruments


def load_midi(filename):
    pass

# etc.
