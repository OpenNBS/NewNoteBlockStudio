from typing import Optional

from PyQt5.QtWidgets import QFileDialog


def getLoadSongDialog(parent=None) -> Optional[str]:
    filename, _filter = QFileDialog.getOpenFileName(
        parent=parent,
        caption="Load song",
        directory="",
        filter="Note Block Songs (*.nbs)",
    )
    return filename
