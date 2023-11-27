from typing import List, Tuple

from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5 import QtCore, QtQuick

from nbs.core.data import Note
from nbs.core.file import load_song


class NoteManager(QtCore.QObject):
    notesChanged = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self._notes = []

        self._notes.append({"tick": 0, "layer": 0, "instrument": 0, "key": 35})
        self._notes.append({"tick": 4, "layer": 0, "instrument": 1, "key": 36})
        self._notes.append({"tick": 8, "layer": 0, "instrument": 2, "key": 37})
        self._notes.append({"tick": 12, "layer": 0, "instrument": 3, "key": 38})

    @QtCore.pyqtProperty("QVariantList", notify=notesChanged)
    def notes(self):
        return self._notes

    @notes.setter
    def notes(self, value: List[Note]):
        if self._notes != value:
            self._notes = value
            self.notesChanged.emit()

    @QtCore.pyqtSlot(str)
    def loadSong(self, path: str):
        print("Loading song:", path)
        song = load_song(ApplicationContext().get_resource(path))

        print("Loaded song")

        new_notes = [
            {
                "tick": note.tick,
                "layer": note.layer,
                "instrument": note.instrument,
                "key": note.key,
            }
            for note in song.notes[:100]
        ]
        print("New notes: ", len(new_notes))

        self.notes = new_notes


if __name__ == "__main__":
    pass
