import pynbs


def save_nbs(song, location):
    """Write the specified song object to a .nbs file at the specified location.
    "location" is an absolute path to the save location."""
    file = pynbs.new_file(**song.header)

    file.notes.extend(song.notes)
    file.layers.extend(song.layers)
    file.instruments.extend(song.custom_instruments)

    file.save(location)
