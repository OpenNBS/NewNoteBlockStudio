import nbs.core.scripts.loader as loader


class Song:
    """Object which holds all the data about the song currently editing.
    song_dict is temporary until I update the pynbs package."""
    def __init__(self, filename=None, song_dict=None):
        self.header = None
        self.notes = None
        self.layers = None
        self.instruments = None

        self.undo = []  # future

        if filename:
            self.load_song(filename)
        elif song_dict:
            self.header = song_dict["header"]
            self.notes = song_dict["notes"]
            self.layers = song_dict["layers"]
            self.instruments = song_dict["instruments"]

    def load_song(self, filename):
        self.header, self.notes, self.layers, self.instruments = loader.load_nbs(filename)
