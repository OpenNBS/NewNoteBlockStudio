from typing import Optional

from PyQt5 import QtWidgets


def getLoadSongDialog(parent: Optional[QtWidgets.QWidget] = None) -> Optional[str]:
    filename, _filter = QtWidgets.QFileDialog.getOpenFileName(
        parent=parent,
        caption="Load song",
        directory="",
        filter="Note Block Songs (*.nbs)",
    )
    return filename


def getSaveSongDialog(parent: Optional[QtWidgets.QWidget] = None) -> Optional[str]:
    filename, _filter = QtWidgets.QFileDialog.getSaveFileName(
        parent=parent,
        caption="Save song",
        directory="",
        filter="Note Block Songs (*.nbs)",
    )
    return filename
