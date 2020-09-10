from nbs.core.scripts.load import load_nbs
from nbs.core.scripts.save import save_nbs


class Instrument():
    def __init__(self, name, sound="", press=False):
        self.name = ""
        self.sound = sound
        self.press = press
        self.icon = None

    def load(self):
        pass


class Song:
    """Object which holds all the data about the song currently editing."""
    def __init__(self, filename=None):
        self.header = {}
        self.notes = []
        self.layers = []
        self.custom_instruments = []
        self.location = ""

        self.undo = []  # future

        if filename:
            header, self.notes, self.layers, self.custom_instruments = load_nbs(filename)
            self.header["version"] = header.version
            self.header["default_instruments"] = header.default_instruments
            self.header["song_length"] = header.song_length
            self.header["song_layers"] = header.song_layers
            self.header["song_name"] = header.song_name
            self.header["song_author"] = header.song_author
            self.header["original_author"] = header.original_author
            self.header["description"] = header.description
            self.header["tempo"] = header.tempo
            self.header["auto_save"] = header.auto_save
            self.header["auto_save_duration"] = header.auto_save_duration
            self.header["time_signature"] = header.time_signature
            self.header["minutes_spent"] = header.minutes_spent
            self.header["left_clicks"] = header.left_clicks
            self.header["right_clicks"] = header.right_clicks
            self.header["blocks_added"] = header.blocks_added
            self.header["blocks_removed"] = header.blocks_removed
            self.header["song_origin"] = header.song_origin
            self.location = filename

    def save(self, location=None):
        """Saves the song in .nbs format to the location specified."""
        if not location:
            location = self.location
        save_nbs(self, location)
