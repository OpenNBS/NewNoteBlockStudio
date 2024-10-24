from typing import Callable

from PyQt5 import QtCore, QtGui


class ScrollingPaintCache:
    def __init__(
        self,
        height: int,
        paintFunction: Callable[[QtGui.QPainter, QtCore.QRect], None],
        width: int = 2000,
    ):
        self.width = width
        self.height = height

        self.start = 0
        self.end = self.width

        self.pixmap = QtGui.QPixmap()
        self.painter = QtGui.QPainter(self.pixmap)
        self.paintFunction = paintFunction

    def paint(self, paintDevice: QtGui.QPaintDevice, startPos: int, width: int, rect: QtCore.QRect):

        # print(startPos, width, self.start, self.end)

        if startPos < self.start or startPos + width > self.end:
            self.reset()
            if width > self.width:
                self.width = width * 2
        #    print("Redrawing (cache was out of bounds)")

        if self.pixmap.isNull():
            self.start = startPos  # TODO: when scrolling backwards, the cache is useless (draw a bit behind the starting point as well)
            self.end = startPos + self.width
            self._repaint(painter=self.painter)
        #    print("Redrawing (cache was null)")

        # else:
        #    print("Using cache")

        self.painter.begin(paintDevice)

        sourceRect = QtCore.QRect(startPos - self.start + rect.x(), rect.y(), rect.width(), rect.height())
        self.painter.drawPixmap(
            rect,
            self.pixmap,
            sourceRect,
        )
        self.painter.end()

    def _repaint(self, painter: QtGui.QPainter):
        rect = QtCore.QRect(0, 0, self.width, self.height)
        self.pixmap.swap(QtGui.QPixmap(self.width, self.height))
        self.painter.begin(self.pixmap)
        self.paintFunction(painter, rect)
        self.painter.end()

    def reset(self):
        self.pixmap.swap(QtGui.QPixmap())
