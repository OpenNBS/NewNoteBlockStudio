import nbs.core.scripts.loader as loader


class Song:
    """Object which holds all the data about the song currently editing."""
    def __init__(self, filename=None):
        self.header = {}
        self.notes = []
        self.layers = []
        self.custom_instruments = []

        self.undo = []  # future

        if filename:
            self.load_song(filename)

    def load_song(self, filename):
        self.header, self.notes, self.layers, self.custom_instruments = loader.load_nbs(filename)
