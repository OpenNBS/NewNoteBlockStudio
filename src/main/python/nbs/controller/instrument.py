import colorsys
import os
from dataclasses import dataclass, field
from random import randint
from typing import Any, List, Optional, Sequence, Tuple, Union
from uuid import UUID, uuid4

from PyQt5 import QtCore, QtGui

from nbs.core.context import appctxt
from nbs.core.data import Instrument, default_instruments

Color = Tuple[int, int, int]
PathLike = Union[str, bytes, os.PathLike]


def random_color() -> Color:
    return colorsys.hsv_to_rgb(
        randint(0, 359),
        randint(50, 100),
        randint(50, 100),
    )


def load_default_icon(path: PathLike) -> QtGui.QIcon:
    try:
        return QtGui.QIcon(appctxt.get_resource(f"images/instruments/{path}"))
    except FileNotFoundError:
        raise FileNotFoundError(f"Icon {path} not found")


def load_custom_icon(id: int) -> QtGui.QIcon:
    # TODO: generate custom icon based on id
    return load_default_icon("harp.png")


def loadBlockPixmap(color: Color) -> QtGui.QPixmap:
    pixmap = QtGui.QPixmap(32, 32)
    painter = QtGui.QPainter(pixmap)
    painter.setBrush(QtGui.QColor(*color))
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
            self.icon = load_custom_icon(self.id)
        self.blockPixmap = loadBlockPixmap(self.__instrument.color)
        self.blockCount = 0
        self.loaded = False
        self.isDefault = False

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

    instrumentListUpdated = QtCore.pyqtSignal(list)

    instrumentSoundLoadRequested = QtCore.pyqtSignal(str)

    def __init__(
        self, instruments: Sequence[Instrument], parent: Optional[QtCore.QObject] = None
    ) -> None:
        super().__init__(parent)
        self.noteBlockPixmap = QtGui.QPixmap(":/images/note_block.png")
        self.instruments: List[InstrumentInstance] = []
        if instruments:
            self.loadInstrumentsFromList(instruments)

    def loadInstrumentsFromList(self, instruments: Sequence[Instrument]) -> None:
        # TODO: use later for importing instruments from nbs file
        for ins in instruments:
            self.loadInstrument(ins)

    def loadInstrument(self, ins: Instrument) -> InstrumentInstance:
        """Load an instrument into the instrument list, and return the added `InstrumentInstance`."""
        # icon = load_icon(ins.icon_path)
        # iconPixmap = paint_icon(self.noteBlockPixmap, color)
        instrumentInstance = InstrumentInstance(
            id=len(self.instruments),
            instrument=ins,
        )
        self.instruments.append(instrumentInstance)
        return instrumentInstance

    @QtCore.pyqtSlot()
    def createInstrument(self) -> None:
        customId = len(self.instruments) - len(default_instruments) + 1
        instrument = Instrument(
            name=f"Custom Instrument #{customId}",
            color=random_color(),
        )
        self.addInstrument(instrument)

    @QtCore.pyqtSlot(Instrument)
    def addInstrument(self, ins: Instrument) -> None:
        instrumentInstance = self.loadInstrument(ins)
        self.instrumentAdded.emit(instrumentInstance)
        self.instrumentSoundLoadRequested.emit(ins.sound_path)
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
