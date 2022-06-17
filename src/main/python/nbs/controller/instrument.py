import colorsys
import os
from dataclasses import dataclass, field
from random import randint
from typing import Optional, Sequence, Tuple, Union
from uuid import UUID, uuid4

from nbs.core.data import Instrument
from PyQt5 import QtCore, QtGui

Color = Tuple[int, int, int]
PathLike = Union[str, bytes, os.PathLike]


def random_color() -> Color:
    return colorsys.hsv_to_rgb(
        randint(0, 359),
        randint(50, 100),
        randint(50, 100),
    )


def load_icon(path: PathLike) -> QtGui.QPixmap:
    try:
        return QtGui.QPixmap(path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Icon {path} not found")


def paint_icon(pixmap: QtGui.QPixmap, color: Color) -> QtGui.QPixmap:
    painter = QtGui.QPainter(pixmap)
    painter.setBrush(QtGui.QColor(*color))
    painter.drawRect(0, 0, pixmap.width(), pixmap.height())


class InstrumentInstance:
    def __init__(
        self,
        id: int,
        name: str,
        press: Optional[bool] = False,
        color: Optional[Color] = None,
        icon: Optional[QtGui.QPixmap] = None,
        soundPath: Optional[PathLike] = None,
    ) -> None:
        self.id = id
        self.name = name
        self.press = press
        color = color or random_color()
        self.icon = icon
        self.soundPath = soundPath
        self.blockCount = 0

    @property
    def loaded(self):
        if self.sound is None:
            return False
        return os.path.exists(self.soundPath)

    # name: str
    # icon: field(init=initIcon)
    # soundPath: Optional[str] = None
    # iconPath: Optional[QtGui.QIcon] = None
    # id: UUID = field(default_factory=uuid4)
    # loaded: bool = False
    # blockCount: int = 0
    # press: bool = False


class InstrumentController(QtCore.QObject):

    instrumentAdded = QtCore.pyqtSignal(Instrument)
    instrumentChanged = QtCore.pyqtSignal(int, Instrument)
    instrumentRemoved = QtCore.pyqtSignal(int)
    instrumentSwapped = QtCore.pyqtSignal(int, int)

    instrumentListUpdated = QtCore.pyqtSignal(list)

    def __init__(self, instruments: Sequence[Instrument], parent=None) -> None:
        super().__init__(parent)
        self.noteBlockPixmap = QtGui.QPixmap(":/images/note_block.png")
        self.instruments = []
        if instruments:
            self.loadInstrumentsFromList(instruments)

    def loadInstrumentsFromList(self, instruments: Sequence) -> None:
        # TODO: use later for importing instruments from nbs file
        for ins in instruments:
            self.loadInstrument(ins.name, ins.color, ins.icon_path, ins.sound_path)

    def loadInstrument(
        self,
        name: str,
        color: Color,
        iconPath: Optional[PathLike] = None,
        soundPath: Optional[PathLike] = None,
    ) -> None:
        icon = load_icon(iconPath)
        iconPixmap = paint_icon(self.noteBlockPixmap, color)
        instrument = InstrumentInstance(
            len(self.instruments), name, color, icon, soundPath
        )
        self.instruments.append(instrument)

    @QtCore.pyqtSlot(Instrument)
    def addInstrument(self, ins: Instrument) -> None:
        self.loadInstrument(ins.name, ins.color, ins.icon_path, ins.sound_path)
        self.instrumentAdded.emit(ins)
        self.instrumentListUpdated.emit(self.instruments)

    @QtCore.pyqtSlot(int)
    def removeInstrument(self, id: int) -> None:
        self.instruments.pop(id)
        self.instrumentRemoved.emit(id)
        self.instrumentListUpdated.emit(self.instruments)

    def swapInstruments(self, id1: int, id2: int) -> None:
        self.instruments[id1], self.instruments[id2] = (
            self.instruments[id2],
            self.instruments[id1],
        )
        self.instrumentSwapped.emit(id1, id2)
        self.instrumentListUpdated.emit(self.instruments)

    def resetInstruments(self) -> None:
        for instrument in self.instruments:
            if instrument.isDefault:
                self.instruments.pop(instrument)

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

    @QtCore.pyqtSlot(int, str)
    def setInstrumentName(self, id: int, name: str) -> None:
        self.instruments[id].name = name

    @QtCore.pyqtSlot(int, tuple)
    def setInstrumentColor(self, id: int, color: Color) -> None:
        self.instruments[id].color = color

    @QtCore.pyqtSlot(int, bool)
    def setInstrumentPress(self, id: int, press: bool) -> None:
        self.instruments[id].press = press
