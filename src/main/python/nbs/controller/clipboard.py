import pickle
from typing import List, Optional

from PyQt5 import QtCore, QtGui

from nbs.core.data import Note

MIMETYPE = "application/nbs-noteblock-selection"


class ClipboardController(QtCore.QObject):

    clipboardChanged = QtCore.pyqtSignal(list)
    clipboardCountChanged = QtCore.pyqtSignal(int)

    def __init__(
        self, clipboard: QtGui.QClipboard, parent: Optional[QtCore.QObject] = None
    ) -> None:
        super().__init__(parent)
        self._clipboard = clipboard

    def _getSelectionMimeData(self, notes: List[Note]) -> QtCore.QMimeData:
        mimeData = QtCore.QMimeData()
        mimeData.setData(
            MIMETYPE,
            QtCore.QByteArray(pickle.dumps(notes)),
        )
        return mimeData

    def _loadSelectionMimeData(self, mimeData: QtCore.QMimeData) -> List[Note]:
        if mimeData.hasFormat(MIMETYPE):
            data: List[Note] = pickle.loads(mimeData.data(MIMETYPE))
            return data
        raise ValueError("MimeData does not contain a valid selection")

    def _setMimeData(self, mimeData: QtCore.QMimeData) -> None:
        if mimeData.hasFormat(MIMETYPE):
            self._clipboard.setMimeData(mimeData)
        else:
            raise ValueError("MimeData does not contain a valid selection")

    def _getMimeData(self) -> QtCore.QMimeData:
        return self._clipboard.mimeData()

    @QtCore.pyqtSlot(list)
    def setContent(self, notes: List[Note]) -> None:
        self._setMimeData(self._getSelectionMimeData(notes))
        self.clipboardChanged.emit(notes)
        self.clipboardCountChanged.emit(len(notes))

    @QtCore.pyqtSlot()
    def getContent(self) -> List[Note]:
        return self._loadSelectionMimeData(self._getMimeData())
