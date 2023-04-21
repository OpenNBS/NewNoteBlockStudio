from typing import Optional

from PyQt5 import QtCore

from nbs.controller.instrument import InstrumentController
from nbs.controller.layer import LayerController
from nbs.controller.playback import PlaybackController
from nbs.core.data import Song, SongHeader


class SongController(QtCore.QObject):

    """
    Object that manages the song data. Delegates updates made to
    the song to the appropriate controller objects. This object is
    the "single source of truth" for the song data.
    """

    def __init__(
        self,
        layerController: LayerController,
        instrumentController: InstrumentController,
        playbackController: PlaybackController,
        parent: Optional[QtCore.QObject] = None,
    ):
        super().__init__(parent)
        # TODO: A NoteController should exist and be here as well
        self.layerController = layerController
        self.instrumentController = instrumentController
        self.song = Song(
            header=SongHeader(),
            notes=[],
            layers=layerController.layers,
            instruments=instrumentController.instruments,
        )

        # For convenience
        self.layers = self.layerController.layers
        self.instruments = self.instrumentController.instruments

    def resetSong(self) -> None:
        self.layerController.resetLayers()
        self.instrumentController.resetInstruments()
        self.playbackController.reset()

    def loadSong(self, song: Song) -> None:
        self.layerController.loadLayers(song.layers)
        self.instrumentController.resetInstruments()
        self.instrumentController.loadInstrumentsFromList(song.instruments)
        self.playbackController.setTempo(song.header.tempo)
