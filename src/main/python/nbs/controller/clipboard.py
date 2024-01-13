import pickle
from typing import List, Optional

from PyQt5 import QtCore, QtGui

from nbs.core.data import Note

MIMETYPE = "application/nbs-noteblock-selection"


def selectionToMimeData(notes: List[Note]) -> QtCore.QMimeData:
    mimeData = QtCore.QMimeData()
    mimeData.setData(
        MIMETYPE,
        QtCore.QByteArray(pickle.dumps(notes)),
    )
    return mimeData


def mimeDataToSelection(mimeData: QtCore.QMimeData) -> List[Note]:
    if not mimeData.hasFormat(MIMETYPE):
        raise ValueError("MimeData does not contain a valid selection")
    data: List[Note] = pickle.loads(mimeData.data(MIMETYPE))
    return data


class ClipboardController(QtCore.QObject):
    clipboardChanged = QtCore.pyqtSignal(list)
    clipboardCountChanged = QtCore.pyqtSignal(int)

    def __init__(
        self, clipboard: QtGui.QClipboard, parent: Optional[QtCore.QObject] = None
    ) -> None:
        super().__init__(parent)
        self._clipboard = clipboard
        self._clipboard.dataChanged.connect(self._onClipboardChanged)
        self._content: List[Note] = []

    def _setMimeData(self, mimeData: QtCore.QMimeData) -> None:
        if mimeData.hasFormat(MIMETYPE):
            self._clipboard.setMimeData(mimeData)
        else:
            raise ValueError("MimeData does not contain a valid selection")

    def _getMimeData(self) -> QtCore.QMimeData:
        return self._clipboard.mimeData()

    def _onClipboardChanged(self) -> None:
        """
        Called when the clipboard content changes, either by a user action or by
        an external program.
        """

        try:
            self._content = mimeDataToSelection(self._clipboard.mimeData())
        except ValueError:
            self._content = []
        self.clipboardChanged.emit(self._content)
        self.clipboardCountChanged.emit(len(self._content))

    @QtCore.pyqtSlot(list)
    def setContent(self, notes: List[Note]) -> None:
        self._setMimeData(selectionToMimeData(notes))
        self.clipboardChanged.emit(notes)
        self.clipboardCountChanged.emit(len(notes))

    @QtCore.pyqtSlot()
    def getContent(self) -> List[Note]:
        return self._content
