import colorsys
import os
import random
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Optional, Sequence, Tuple, Union
from uuid import UUID, uuid4

from PyQt5 import QtCore, QtGui

from nbs.core.context import appctxt
from nbs.core.data import Instrument, default_instruments

Color = Tuple[int, int, int]
PathLike = Union[str, bytes, os.PathLike]


def copy_sound_file(path: Optional[PathLike]) -> Path:
    """
    Copy a sound file to the Sounds folder, and return the new absolute path."""
    print("PATH:", path)
    if path is None:
        return Path("")
    try:
        new_path = appctxt.get_resource(str(Path("sounds", path)))
    except FileNotFoundError:
        if path is None:
            raise FileNotFoundError("Instrument sound path doesn't exist")
        new_path = Path(appctxt.get_resource("sounds"), path)
        print("NEW PATH:", new_path)
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        shutil.copy(
            "C:\\Users\\Bernardo\\Minecraft Note Block Studio\\Data\\Sounds\\" + path,
            new_path,
        )
    return new_path


def random_color() -> Color:
    return tuple(
        round(x * 255)
        for x in colorsys.hsv_to_rgb(
            random.uniform(0, 1),
            random.uniform(0.5, 1),
            random.uniform(0.5, 1),
        )
    )


def id_to_color(id: int) -> Color:
    color_index = id % 16
    hue = color_index / 16
    return tuple(round(x * 255) for x in colorsys.hsv_to_rgb(hue, 0.5, 1))


def load_default_icon(path: PathLike) -> QtGui.QIcon:
    try:
        return QtGui.QIcon(appctxt.get_resource(f"images/instruments/{path}"))
    except FileNotFoundError:
        raise FileNotFoundError(f"Icon {path} not found")


def load_custom_icon(id: int) -> QtGui.QIcon:
    # TODO: generate custom icon based on id
    pixmap = QtGui.QPixmap(appctxt.get_resource("images/instruments/harp.png"))
    painter = QtGui.QPainter(pixmap)
    painter.setPen(QtCore.Qt.GlobalColor.black)
    painter.setBrush(QtGui.QColor(*id_to_color(id)))
    painter.drawRect(6, 6, 17, 17)

    id_padded = str(id + 1).rjust(2, "0")

    # draw semi-transparent black text as shadow
    painter.setOpacity(0.9)
    painter.setFont(QtGui.QFont("Arial", 9, QtGui.QFont.Bold))
    painter.setBrush(QtCore.Qt.GlobalColor.black)
    painter.drawText(7, 7, 17, 17, QtCore.Qt.AlignCenter, id_padded)

    # draw white text on top
    painter.setOpacity(1)
    painter.setPen(QtGui.QPen(QtCore.Qt.GlobalColor.white))
    painter.drawText(6, 6, 17, 17, QtCore.Qt.AlignCenter, id_padded)
    painter.end()
    return QtGui.QIcon(pixmap)


def loadBlockPixmap(color: Color) -> QtGui.QPixmap:
    pixmap = QtGui.QPixmap(32, 32)
    painter = QtGui.QPainter(pixmap)
    painter.setBrush(QtGui.QColor(color[0], color[1], color[2]))
    painter.drawRect(0, 0, pixmap.width(), pixmap.height())
    painter.end()
    return pixmap


class InstrumentInstance:
    def __init__(self, id: int, instrument: Instrument):
        self.__instrument = instrument
        self.id = id
        if self.__instrument.icon_path is not None:
            self.icon = load_default_icon(self.__instrument.icon_path)
        else:
            custom_id = self.id - len(default_instruments)
            self.icon = load_custom_icon(custom_id)
        self.blockPixmap = loadBlockPixmap(self.__instrument.color or random_color())
        self.blockCount = 0
        self.loaded = False
        self.absSoundPath: Optional[Path] = None

    @property
    def isDefault(self) -> bool:
        return self.id < len(default_instruments)

    def __getattr__(self, name: str):
        return getattr(self.__instrument, name)

    def __setattr__(self, attr: str, value: Any) -> None:
        if attr == "_InstrumentInstance__instrument":
            object.__setattr__(self, attr, value)

        return setattr(self.__instrument, attr, value)

    # name: str
    # icon: field(init=initIcon)
    # soundPath: Optional[str] = None
    # iconPath: Optional[QtGui.QIcon] = None
    # id: UUID = field(default_factory=uuid4)
    # loaded: bool = False
    # blockCount: int = 0
    # press: bool = False


class InstrumentController(QtCore.QObject):

    instrumentAdded = QtCore.pyqtSignal(InstrumentInstance)
    instrumentChanged = QtCore.pyqtSignal(int, InstrumentInstance)
    instrumentRemoved = QtCore.pyqtSignal(int)
    instrumentSwapped = QtCore.pyqtSignal(int, int)

    instrumentNameChanged = QtCore.pyqtSignal(int, str)
    instrumentSoundChanged = QtCore.pyqtSignal(int, str)
    instrumentKeyChanged = QtCore.pyqtSignal(int, int)
    instrumentPressChanged = QtCore.pyqtSignal(int, bool)

    instrumentListUpdated = QtCore.pyqtSignal(list)
    currentInstrumentChanged = QtCore.pyqtSignal(int)

    instrumentSoundLoadRequested = QtCore.pyqtSignal(str)

    def __init__(
        self, instruments: Sequence[Instrument], parent: Optional[QtCore.QObject] = None
    ) -> None:
        super().__init__(parent)
        self.noteBlockPixmap = QtGui.QPixmap(":/images/note_block.png")
        self.instruments: List[InstrumentInstance] = []
        if instruments:
            self.loadInstrumentsFromList(instruments)
        self.currentInstrument = 0

    def loadInstrumentsFromList(self, instruments: Sequence[Instrument]) -> None:
        for ins in instruments:
            self.addInstrument(ins)

    def _loadInstrument(self, ins: Instrument) -> InstrumentInstance:
        """
        Load the data for instrument `ins` and add it to the instrument list.
        Return the added `InstrumentInstance`.
        """
        # icon = load_icon(ins.icon_path)
        # iconPixmap = paint_icon(self.noteBlockPixmap, color)

        new_path = copy_sound_file(ins.sound_path)
        instrumentInstance = InstrumentInstance(
            id=len(self.instruments), instrument=ins
        )
        instrumentInstance.absSoundPath = new_path
        self.instruments.append(instrumentInstance)
        return instrumentInstance

    # TODO: clean up this mess of load/add/create
    @QtCore.pyqtSlot()
    def createInstrument(self) -> None:
        """
        Create a new custom instrument with default values, and add it to the instrument list.
        """
        # TODO: change sequential id to UUID
        customId = len(self.instruments) - len(default_instruments) + 1
        instrument = Instrument(
            name=f"Custom Instrument #{customId}",
            color=random_color(),
        )
        self.addInstrument(instrument)

    @QtCore.pyqtSlot(Instrument)
    def addInstrument(self, ins: Instrument) -> None:
        """
        Adds the instrument `ins` to the instrument list, and emits the appropriate signals.
        """
        instrumentInstance = self._loadInstrument(ins)
        self.instrumentSoundLoadRequested.emit(str(instrumentInstance.absSoundPath))
        self.instrumentAdded.emit(instrumentInstance)
        self.instrumentListUpdated.emit(self.instruments)

    @QtCore.pyqtSlot(int)
    def removeInstrument(self, id: int) -> None:
        """
        Remove the instrument with ID `id` from the instrument list,
        emitting the appropriate signals.
        """
        self.instruments.pop(id)
        self.instrumentRemoved.emit(id)
        self.instrumentListUpdated.emit(self.instruments)

    def swapInstruments(self, id1: int, id2: int) -> None:
        """
        Swap the instruments with IDs `id1` and `id2` in the instrument list,
        emitting the appropriate signals.
        """
        self.instruments[id1], self.instruments[id2] = (
            self.instruments[id2],
            self.instruments[id1],
        )
        self.instrumentSwapped.emit(id1, id2)
        self.instrumentListUpdated.emit(self.instruments)

    def resetInstruments(self) -> None:
        """
        Clears all custom instruments from the instrument list and emit the appropriate signals.
        """
        first_custom_id = len(default_instruments)
        while len(self.instruments) > first_custom_id:
            self.instruments.pop()
            self.instrumentRemoved.emit(len(self.instruments))
        self.instrumentListUpdated.emit(self.instruments)

    # TODO: It's probably better to have a single method that takes a dict of
    #       attributes to change, and then emit a signal for each attribute
    #       that changed. This would allow for more flexibility in the future.

    # TODO: It's weird that the main window should be responsible for updating
    #       the instrument block count. It would be better if the instrument controller
    #       was tied to a SongController that had methods to add/remove blocks,
    #       and took care of it for the MainWindow, hiding the complexity (a Facade pattern).

    @QtCore.pyqtSlot(int)
    def addBlockToCount(self, id: int) -> None:
        self.instruments[id].blockCount += 1

    @QtCore.pyqtSlot(int)
    def removeBlockFromCount(self, id: int) -> None:
        self.instruments[id].blockCount -= 1

    def changeBlockCount(self, id: int, amount: int) -> None:
        self.instruments[id].blockCount += amount

    @QtCore.pyqtSlot(int, int)
    def setBlockCount(self, id: int, count: int) -> None:
        self.instruments[id].blockCount = count

    @QtCore.pyqtSlot(int)
    def setCurrentInstrument(self, id: int) -> None:
        if id > len(self.instruments):
            raise IndexError(f"Instrument id out of range: {id}")
        self.currentInstrument = id
        self.currentInstrumentChanged.emit(id)

    @QtCore.pyqtSlot(int, str)
    def setInstrumentName(self, id: int, name: str) -> None:
        self.instruments[id].name = name
        self.instrumentNameChanged.emit(id, name)
        self.instrumentChanged.emit(id, self.instruments[id])
        self.instrumentListUpdated.emit(self.instruments)

    @QtCore.pyqtSlot(int, str)
    def setInstrumentSound(self, id: int, sound: str) -> None:
        ins = self.instruments[id]
        ins.sound_path = copy_sound_file(sound)
        self.instrumentSoundChanged.emit(id, sound)
        self.instrumentSoundLoadRequested.emit(ins.sound_path)
        self.instrumentChanged.emit(id, self.instruments[id])
        self.instrumentListUpdated.emit(self.instruments)

    @QtCore.pyqtSlot(int, int)
    def setInstrumentKey(self, id: int, key: int) -> None:
        self.instruments[id].key = key
        self.instrumentKeyChanged.emit(id, key)
        self.instrumentChanged.emit(id, self.instruments[id])
        self.instrumentListUpdated.emit(self.instruments)

    @QtCore.pyqtSlot(int, bool)
    def setInstrumentPress(self, id: int, press: bool) -> None:
        self.instruments[id].press = press
        self.instrumentPressChanged.emit(id, press)
        self.instrumentChanged.emit(id, self.instruments[id])
        self.instrumentListUpdated.emit(self.instruments)
