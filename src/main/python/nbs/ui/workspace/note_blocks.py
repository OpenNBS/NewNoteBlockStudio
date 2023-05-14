from __future__ import annotations

import math
import pickle
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Generator, List, Optional, Sequence, Union

from PyQt5 import QtCore, QtGui, QtWidgets

from nbs.core.context import appctxt
from nbs.core.data import Instrument, Layer, Note, default_instruments
from nbs.core.utils import *
from nbs.ui.utils.cache import ScrollingPaintCache

from .constants import *

__all__ = ["NoteBlockArea"]


PIXMAP_CACHE = QtGui.QPixmapCache()
NOTE_BLOCK_PIXMAP = QtGui.QPixmap(
    appctxt.get_resource("images/note_block_grayscale.png")
)


instrument_data = default_instruments  # TODO: replace with actual data


class TimeRuler(QtWidgets.QWidget):

    clicked = QtCore.pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(32)
        self.paintCache = ScrollingPaintCache(self.height(), self.paint)
        self.offset: int = 0
        self.scale = 1
        self.tempo = 10.00

    def getTextRect(self, fm: QtGui.QFontMetrics, text, x=0, y=0):
        # Calling boundingRect just once returns a wrong size. See:
        # https://stackoverflow.com/a/32078341/9045426
        textRect = fm.boundingRect(text)
        textRect = fm.boundingRect(
            textRect, 0, text
        )  # TODO: Slow as hell, optimize. Maybe precalculate the bounding rects?
        textRect.moveCenter(QtCore.QPoint(round(x), round(y)))
        # if textRect.left() < 0 and textRect.right() >= (textRect.width() / 2):
        #    textRect.moveLeft(1)
        # if textRect.right() > rect.width():
        #    textRect.moveRight(textRect.width() - 1)
        return textRect

    def paintEvent(self, event: QtGui.QPaintEvent):
        self.resize(self.parent().width(), self.height())
        self.paintCache.paint(self, self.offset, self.width())

    def paint(self, painter: QtGui.QPainter, rect: QtCore.QRect):
        mid = rect.height() // 2
        blocksize = BLOCK_SIZE * self.scale
        fm = painter.fontMetrics()
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(QtCore.Qt.GlobalColor.white)
        painter.drawRect(rect)
        painter.setPen(QtCore.Qt.GlobalColor.black)
        painter.drawLine(rect.bottomLeft(), rect.bottomRight())
        painter.drawLine(rect.left(), mid, rect.right(), mid)
        startTick, startPos = divmod(self.offset, blocksize)
        # Bottom part
        # We start on negative coordinates to fill the gap until the first visible line
        x = -startPos
        y = (mid + rect.bottom()) / 2 - 1
        while x <= rect.width():
            painter.drawLine(x, rect.bottom() - 2, x, rect.bottom())
            currentTick = startTick + round((startPos + x) / blocksize)
            if currentTick % 4 == 0:
                text = str(int(currentTick))
                textRect = self.getTextRect(fm, text, round(x), y)
                painter.drawText(
                    textRect,
                    QtCore.Qt.AlignmentFlag.AlignHCenter
                    | QtCore.Qt.AlignmentFlag.AlignTop,
                    text,
                )
            x += blocksize
        # Top part
        # We start with the length occupied by 250ms on the song, then double it
        # (essentially halving the number of markings) until they're far enough apart
        timeInterval = 0.25
        distance = int(self.tempo / 4 * blocksize)
        minDistance = self.getTextRect(fm, seconds_to_timestr(0)).width() + 50
        while distance < minDistance:
            distance *= 2
            timeInterval *= 2
        startTime, startPos = divmod(self.offset, distance)
        startTime *= timeInterval
        for i, x in enumerate(range(-startPos, rect.width() + minDistance, distance)):
            painter.drawLine(x, mid - 2, x, mid)
            time = startTime + i * timeInterval
            text = seconds_to_timestr(time)
            y = mid / 2 - 1
            textRect = self.getTextRect(fm, text, x, y)
            painter.drawText(
                textRect,
                QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignTop,
                text,
            )

    def mouseReleaseEvent(self, event):
        pos = event.pos().x()
        tick = (pos + self.offset) / (self.scale * BLOCK_SIZE)
        self.clicked.emit(tick)
        self.update()

    @QtCore.pyqtSlot(int)
    def setOffset(self, value):
        self.offset = value
        self.update()

    @QtCore.pyqtSlot(float)
    def setScale(self, value):
        self.scale = value
        self.paintCache.reset()
        self.update()

    @QtCore.pyqtSlot(float)
    def setTempo(self, newTempo: float):
        self.tempo = newTempo
        self.paintCache.reset()
        self.update()


class Marker(QtWidgets.QWidget):

    moved = QtCore.pyqtSignal(float)

    def __init__(self, parent: Optional[QtCore.QObject] = None) -> None:
        super().__init__(parent)
        self.tick = 0
        self.offset = 0
        self.scale = 1
        self.setMouseTracking(True)
        self.setCursor(QtCore.Qt.CursorShape.SizeHorCursor)
        self.setFixedHeight(800)
        self.setFixedWidth(16)
        self.raise_()

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter()
        painter.begin(self)
        markerColor = QtCore.Qt.GlobalColor.black
        pen = QtGui.QPen(markerColor)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(8, 0, 8, self.height())
        painter.fillPath(self.getMarkerHead(), QtGui.QBrush(markerColor))
        painter.end()

    def getMarkerHead(self) -> QtGui.QPainterPath:
        point1 = QtCore.QPoint(0, 0)
        point2 = QtCore.QPoint(16, 0)
        point3 = QtCore.QPoint(8, 16)
        shape = QtGui.QPolygon([point1, point2, point3])
        region = QtGui.QRegion(shape)
        path = QtGui.QPainterPath()
        path.addRegion(region)
        return path

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        # The event pos is relative to the bounding box of the widget, so we calculate
        # how much it should move based on how far from the center the mouse moved
        if event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            offset = event.pos().x()
            tick = self.posToTick(self.pos().x() + offset)
            self.setTick(tick)
            self.moved.emit(tick)

    def posToTick(self, pos: int) -> float:
        return (pos + self.offset) / (self.scale * BLOCK_SIZE)

    def tickToPos(self, tick: float) -> int:
        return round(tick * self.scale * BLOCK_SIZE) - self.width() // 2 - self.offset

    def updatePos(self) -> None:
        self.move(self.tickToPos(self.tick), 0)

    @QtCore.pyqtSlot(float)
    def setTick(self, tick: float) -> None:
        """Set the position of the marker, in ticks."""
        self.tick = max(0, tick)
        self.updatePos()

    @QtCore.pyqtSlot(int)
    def setOffset(self, offset: int) -> None:
        self.offset = offset
        self.updatePos()

    @QtCore.pyqtSlot(float)
    def setScale(self, scale: float) -> None:
        self.scale = scale
        self.updatePos()


class ScrollMode(Enum):
    """Enum for the different scroll modes for `NoteBlockView`."""

    NONE = 0
    PAGE_BY_PAGE = 1
    TICK_BY_TICK = 2


class NoteBlockView(QtWidgets.QGraphicsView):

    scaleChanged = QtCore.pyqtSignal(float)
    playbackPositionChanged = QtCore.pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent, objectName=__class__.__name__)
        self.currentScale = 1
        self.scrollMode = ScrollMode.PAGE_BY_PAGE
        self.ruler = TimeRuler(parent=self)
        self.marker = Marker(parent=self)

        self.setViewportMargins(0, 32, 0, 0)
        self.setTransformationAnchor(
            QtWidgets.QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.viewport().setObjectName(self.objectName() + "Viewport")
        self.viewport().installEventFilter(self)

        self.horizontalScrollBar().valueChanged.connect(self.ruler.setOffset)
        self.horizontalScrollBar().valueChanged.connect(self.marker.setOffset)
        self.scaleChanged.connect(self.ruler.setScale)
        self.scaleChanged.connect(self.marker.setScale)

        self.ruler.clicked.connect(self.playbackPositionChanged)
        self.marker.moved.connect(self.playbackPositionChanged)

    @QtCore.pyqtSlot(float)
    def setTempo(self, tempo: float) -> None:
        self.ruler.setTempo(tempo)

    @QtCore.pyqtSlot(float)
    def setPlaybackPosition(self, tick):
        self.marker.setTick(tick)
        self.scene().doPlayback(tick)
        self.updateScroll(int(tick * BLOCK_SIZE))

    @QtCore.pyqtSlot()
    def setScale(self, value):
        self.resetTransform()
        self.currentScale = 1
        self.changeScale(value)

    @QtCore.pyqtSlot()
    def changeScale(self, factor):
        if 0.2 < self.currentScale * factor < 4:
            # TODO: Zoom in/out anyway, capping at the max/min scale level
            # Round the factor so that multiplying it by 32 results in a whole number
            newFactor = round(self.currentScale * factor * BLOCK_SIZE) / (
                self.currentScale * BLOCK_SIZE
            )
            self.scale(newFactor, newFactor)
            self.currentScale *= newFactor
            self.scaleChanged.emit(self.currentScale)

    def wheelEvent(self, event):
        if event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier:
            if event.angleDelta().y() > 0:
                self.changeScale(1.2)
            else:
                self.changeScale(1 / 1.2)
        else:
            super().wheelEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Resize vertical scrollbar so it doesn't span the ruler at the top
        vsb = self.verticalScrollBar()
        vsb.move(0, 32)
        vsb.resize(QtCore.QSize(vsb.width(), self.height() - 32 - SCROLL_BAR_SIZE))
        self.ruler.update()
        self.scene().updateSceneSize()

    ########## Auto-scroll ##########

    @QtCore.pyqtSlot(int)
    def setScrollMode(self, mode: int) -> None:
        self.scrollMode = mode

    @QtCore.pyqtSlot(int)
    def updateScroll(self, newPos: int) -> None:
        """
        Update the view's horizontal scroll position to match `newPos`, in pixels,
        according to the view's scroll mode.
        """

        viewport = self.viewport()
        viewYCenter = round(
            self.mapToScene(viewport.rect().center()).y() + 1
        )  # The +1 is to avoid rounding errors

        if newPos == 0:
            return  # Don't scroll when stopping playback

        if self.scrollMode == ScrollMode.NONE:
            return

        elif self.scrollMode == ScrollMode.PAGE_BY_PAGE:
            point = QtCore.QPoint(newPos, viewYCenter)
            if not self.mapToScene(viewport.rect()).containsPoint(point, 0):
                viewWidth = viewport.width()
                self.ensureVisible(
                    newPos, viewYCenter, viewWidth, 0, xMargin=0, yMargin=0
                )

        elif self.scrollMode == ScrollMode.TICK_BY_TICK:
            self.centerOn(newPos, viewYCenter)


class NoteBlockArea(QtWidgets.QGraphicsScene):
    """
    A scrolling area that holds the note blocks in a song.
    """

    ########## Private slots ##########
    sceneSizeChanged = QtCore.pyqtSignal(int, int)
    songHeightChanged = QtCore.pyqtSignal(int)
    songLengthChanged = QtCore.pyqtSignal(int)
    playbackPositionChanged = QtCore.pyqtSignal(int)

    ########## Public slots ##########
    selectionChanged = QtCore.pyqtSignal(int)
    selectionCopied = QtCore.pyqtSignal(list)
    selectAllLeftActionEnabled = QtCore.pyqtSignal(bool)
    selectAllRightActionEnabled = QtCore.pyqtSignal(bool)
    blockCountChanged = QtCore.pyqtSignal(int)
    blockAdded = QtCore.pyqtSignal(int, int, int, int, int)
    tickPlayed = QtCore.pyqtSignal(list)

    def __init__(self, layers: Sequence[Layer], menu: QtWidgets.QMenu, parent=None):
        super().__init__(parent, objectName=__class__.__name__)
        self.view = NoteBlockView(self)
        self.layers = layers
        self.menu = menu
        self.selection = QtWidgets.QRubberBand(
            QtWidgets.QRubberBand.Shape.Rectangle, parent=self.view.viewport()
        )
        self.selection.hide()
        self.selection.setGeometry(0, 0, 0, 0)
        self.selectionStart = None
        self.isDraggingSelection = False
        self.isClearingSelection = False
        self.isMovingBlocks = False
        self.isRemovingNote = False
        self.isClosingMenu = False
        self.menuClickPos = None
        self.scrollSpeedX = 0
        self.scrollSpeedY = 0
        self.activeKey = 45
        self.playingBlocks = set()
        self.previousPlaybackPosition = 0
        self.currentInstrument = 0
        self.minimumLayerCount = 0
        # A value of 12 will generate segments of approximately 4x4 grid spaces,
        # which can be guaranteed to contain 0-10 notes on average.
        # See: https://doc.qt.io/qt-6/qgraphicsscene.html#bspTreeDepth-prop
        self.setBspTreeDepth(12)
        self.initUI()
        self.initPlayback()

        self.tickIndex: Dict[int, List[NoteBlock]] = {}

    ########## UI ##########

    def initUI(self):
        self.updateSceneSize()
        self.installEventFilter(self)
        self.initMenu()
        self.view.setAlignment(
            QtCore.Qt.AlignmentFlag(
                QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignLeft
            )
        )
        self.view.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.startTimer(10)

    def drawBackground(self, painter: QtGui.QPainter, rect: QtCore.QRectF):
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(QtGui.QColor(240, 240, 240))
        painter.drawRect(rect)
        painter.setPen(QtCore.Qt.PenStyle.SolidLine)
        start = int(rect.x() // BLOCK_SIZE)
        end = int(rect.right() // BLOCK_SIZE + 1)
        for x in range(start, end):
            if x % 4 == 0:
                painter.setPen(QtGui.QColor(181, 181, 181))
            else:
                painter.setPen(QtGui.QColor(216, 216, 216))
            painter.drawLine(
                x * BLOCK_SIZE, round(rect.y()), x * BLOCK_SIZE, round(rect.bottom())
            )

    def drawForeground(self, painter: QtGui.QPainter, rect: QtCore.QRectF) -> None:
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(QtCore.Qt.GlobalColor.black)
        painter.setOpacity(0.25)
        for id, layer in enumerate(self.layers):
            if layer.lock:
                painter.drawRect(self.getLayerRegion(id))

    ########## MENU ##########

    def initMenu(self):
        # Dismissing a menu should "cancel" the next click, but triggering an option should not.
        self.menu.aboutToHide.connect(self.onDismissMenu)
        self.menu.triggered.connect(self.onTriggerMenu)

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent) -> None:
        self.menuClickPos = event.scenePos()
        self.toggleSelectLeftRightActions(event.scenePos().x())
        self.menu.exec(event.screenPos())
        return super().contextMenuEvent(event)

    @QtCore.pyqtSlot()
    def onDismissMenu(self):
        self.isClosingMenu = True

    def onTriggerMenu(self):
        self.isClosingMenu = False

    def toggleSelectLeftRightActions(self, pos: int):
        bbox = self.itemsBoundingRect()
        self.selectAllLeftActionEnabled.emit(pos > bbox.left())
        self.selectAllRightActionEnabled.emit(pos < bbox.right())

    ########## SLOTS ##########

    @QtCore.pyqtSlot(int)
    def setActiveKey(self, key):
        self.activeKey = key

    @QtCore.pyqtSlot(float)
    def setTempo(self, tempo):
        self.tempo = tempo

    ########## COORDINATE TRANSFORMATION ##########

    def updateSceneSize(self):
        if len(self.items()) >= 1:
            bbox = self.itemsBoundingRect()
        else:
            bbox = QtCore.QRectF(0, 0, 0, 0)
        viewSize = self.view.rect()
        width = math.ceil((bbox.right() + viewSize.width()) / BLOCK_SIZE)
        height = math.ceil((bbox.bottom() + viewSize.height()) / BLOCK_SIZE)
        height = max(height, self.minimumLayerCount)
        print("Calculated height:", height, "Min. count:", self.minimumLayerCount)
        self.setSceneRect(QtCore.QRectF(0, 0, width * BLOCK_SIZE, height * BLOCK_SIZE))
        self.sceneSizeChanged.emit(width, height)
        print(f"Scene size changed to {width}x{height}")

        # left edge of the rightmost block
        songHeight = int(max((bbox.bottom() // BLOCK_SIZE) - 1, 0))
        # top edge of the bottommost block
        songLength = int(max((bbox.right() // BLOCK_SIZE) - 1, 0))
        self.songHeightChanged.emit(songHeight)
        self.songLengthChanged.emit(songLength)

    def getGridPos(self, point):
        """
        Return the grid coordinates of a position in the scene.

        Args:
            point (QtCore.QPoint): the position to be converted

        Returns:
            tuple (int, int)
        """
        x = point.x() // BLOCK_SIZE
        y = point.y() // BLOCK_SIZE
        return x, y

    def getScenePos(self, x: int, y: int):
        """Return the top left scene position of a set of grid coordinates."""
        return QtCore.QPoint(x * BLOCK_SIZE, y * BLOCK_SIZE)

    def blockAtPos(self, pos: Union[QtCore.QPoint, QtCore.QPointF]):
        viewPos = self.view.mapFromScene(pos)
        viewTransform = self.view.transform()
        return self.itemAt(viewPos, viewTransform)

    ########## SONG ##########

    def reset(self) -> None:
        self.clear()
        self.updateSceneSize()
        self.updateBlockCount()
        self.view.ensureVisible(0, 0, 0, 0)

    def loadNoteData(self, blocks: Sequence[NoteBlock]) -> None:
        self.reset()
        for block in blocks:
            self.addBlock(
                block.tick,
                block.layer,
                block.key,
                block.instrument,
                block.velocity,
                block.panning,
                block.pitch,
            )
        self.updateBlockCount()
        self.updateSceneSize()

    def getNoteData(self) -> List[NoteBlock]:
        blocks = []
        for block in self.items():
            note = NoteBlock(
                block.tick,
                block.layer,
                block.key,
                block.instrument,
                block.velocity,
                block.panning,
                block.pitch,
            )
            blocks.append(note)
        return blocks

    ########## ATOMIC OPERATIONS ##########

    # These methods are used to perform operations on the scene that must be done
    # through these methods. This is to ensure that the scene is always in a valid
    # state, and that the index is always up to date.

    def _doAddBlock(self, block: NoteBlock):
        """Add a note block at the specified position. This operation must always
        be called when adding a block."""
        self.addItem(block)
        tick = block.tick
        if tick not in self.tickIndex:
            self.tickIndex[tick] = []
        self.tickIndex[tick].append(block)

    def _doMoveBlock(self, block: NoteBlock, x: int, y: int):
        """Move a note block by the specified number of grid spaces. This operation must always
        be called when moving a block."""
        prevTick = block.tick
        block.moveBy(x * BLOCK_SIZE, y * BLOCK_SIZE)
        if x != 0:
            self.tickIndex[prevTick].remove(block)
            nextTick = block.tick
            if nextTick not in self.tickIndex:
                self.tickIndex[nextTick] = []
            self.tickIndex[nextTick].append(block)

    def _doRemoveBlock(self, block: NoteBlock):
        """Remove a note block from the scene. This operation must always
        be called when removing a block."""
        self.removeItem(block)
        tick = block.tick
        self.tickIndex[tick].remove(block)

    ########## NOTE BLOCKS ##########

    # These methods are meant to be called externally to perform operations on the
    # scene. They will call the atomic operations above to ensure that the scene is
    # always in a valid state.

    def clear(self):
        """Clear all note blocks in the scene."""
        for item in self.items():
            self._doRemoveBlock(item)

    def addBlock(self, x: int, y: int, *args, **kwargs):
        """Add a note block at the specified position."""
        blockPos = self.getScenePos(x, y)
        block = NoteBlock(x, y, *args, **kwargs)
        block.setPos(blockPos)
        self._doAddBlock(block)
        return block

    def addBlockManual(self, x, y, *args, **kwargs):
        block = self.addBlock(x, y, *args, **kwargs)
        self.updateBlockCount()
        self.updateSceneSize()
        self.blockAdded.emit(block.ins, block.key, block.vel, block.pan, block.pit)

    def removeBlock(self, block: NoteBlock) -> None:
        self._doRemoveBlock(block)
        self.updateBlockCount()
        # TODO: self.blockRemoved.emit()

    def removeBlockAt(self, x: int, y: int) -> None:
        """Remove the note block at the specified position."""
        pos = self.getScenePos(x, y)
        itemAtPos = self.itemAt(pos, self.view.transform())
        if itemAtPos is not None:
            self._doRemoveBlock(itemAtPos)

    def removeBlockManual(self, x: int, y: int) -> None:
        self.removeBlockAt(x, y)
        self.updateSceneSize()

    def updateBlockCount(self):
        self.blockCountChanged.emit(len(self.items()))

    ########## SELECTION ##########

    def setBlocksSelected(self, blocks: Sequence[NoteBlock], selected: bool = True):
        for block in blocks:
            block.setSelected(selected)
        self.updateSelectionStatus()

    def setAreaSelected(self, area: QtCore.QRectF, selected: bool = True):
        # There's no native way of subtracting an area from the current selection, so we use
        # Qt's native implementation to add items (faster), but remove items individually.
        if selected:
            path = QtGui.QPainterPath()
            path.addRect(QtCore.QRectF(area))
            self.setSelectionArea(path, selected)
        else:
            self.setBlocksSelected(self.items(area), False)
        self.updateSelectionStatus()

    def hasSelection(self):
        return len(self.selectedItems()) > 0

    def updateSelectionStatus(self):
        if len(self.items()) == 0:
            self.selectionStatus = -2
        elif self.hasSelection():
            if len(self.selectedItems()) == len(self.items()):
                self.selectionStatus = 1
            else:
                self.selectionStatus = 0
        else:
            self.selectionStatus = -1
        self.selectionChanged.emit(self.selectionStatus)

    def selectionBoundingRect(self) -> QtCore.QRectF:
        rect = QtCore.QRectF()
        for selectedItem in self.selectedItems():
            rect = rect.united(selectedItem.sceneBoundingRect())
        return rect

    @QtCore.pyqtSlot()
    def selectAll(self):
        self.setAreaSelected(self.sceneRect())

    @QtCore.pyqtSlot()
    def deselectAll(self):  # clearSelection/placeSelection
        if self.hasSelection():
            self._clearBlocksUnderSelection()
            # TODO: Collision check takes too long
            self.clearSelection()
            self.updateSceneSize()

    @QtCore.pyqtSlot()
    def deselectAllManual(self):
        if self.hasSelection():
            # This is done to prevent the next mouse
            # release from adding a note block
            self.isClearingSelection = True
            self.deselectAll()

    def _clearBlocksUnderSelection(self):
        for item in self.selectedItems():
            for i in item.collidingItems():
                self.removeBlock(i)

    @QtCore.pyqtSlot()
    def invertSelection(self):
        unselected = []
        for block in self.items():
            if not block.isSelected():
                unselected.append(block)
        self.deselectAll()
        self.setBlocksSelected(unselected, True)

    def moveSelection(self, x: int, y: int):
        for block in self.selectedItems():
            self._doMoveBlock(block, x, y)

    def setSelectionTopLeft(self, point: Union[QtCore.QPoint, QtCore.QPointF]):
        tl = self.selectionBoundingRect().topLeft()
        offsetX = (point.x() - tl.x()) // BLOCK_SIZE
        offsetY = (point.y() - tl.y()) // BLOCK_SIZE
        self.moveSelection(offsetX, offsetY)

    @QtCore.pyqtSlot()
    def selectAllLeft(self, pos: Optional[Union[QtCore.QPoint, QtCore.QPointF]] = None):
        self.deselectAll()
        if pos is None:
            pos = self.menuClickPos.x()
        height = self.height()
        area = QtCore.QRectF(0, 0, pos, height)
        self.setAreaSelected(area)

    @QtCore.pyqtSlot()
    def selectAllRight(
        self, pos: Optional[Union[QtCore.QPoint, QtCore.QPointF]] = None
    ):
        self.deselectAll()
        if pos is None:
            pos = self.menuClickPos.x()
        width = self.width()
        height = self.height()
        area = QtCore.QRectF(pos, 0, width, height)
        self.setAreaSelected(area)

    def expandSelection(self):
        bbox = self.selectionBoundingRect()
        origin = bbox.topLeft()

        for block in self.selectedItems():
            relativePosX = int(block.x() - origin.x() // BLOCK_SIZE)
            self._doMoveBlock(block, relativePosX, 0)

    def compressSelection(self):
        bbox = self.selectionBoundingRect()
        origin = bbox.topLeft()

        for block in self.selectedItems():
            relativePosX = block.x() - origin.x()
            distance = int((-relativePosX / 2) // BLOCK_SIZE)
            self._doMoveBlock(block, distance, 0)

        for block in self.selectedItems():
            while block.collidingItems():
                self._doMoveBlock(block, 0, 1)

    @QtCore.pyqtSlot()
    def deleteSelection(self):
        for block in self.selectedItems():
            self.removeBlock(block)
        self.updateSelectionStatus()
        self.updateSceneSize()

    ########## INSTRUMENTS ##########

    @QtCore.pyqtSlot(int)
    def setCurrentInstrument(self, id_: int):
        self.currentInstrument = id_

    @QtCore.pyqtSlot(int)
    def changeSelectionInstrument(self, id_: int):
        for block in self.selectedItems():
            block.setInstrument(id_)

    ########## CLIPBOARD ##########

    def getSelectionData(self) -> Generator[Note, None, None]:
        origin = self.selectionBoundingRect().topLeft()
        for block in self.selectedItems():
            if isinstance(block, NoteBlock):
                x = (block.x() - origin.x()) // BLOCK_SIZE
                y = (block.y() - origin.y()) // BLOCK_SIZE
                # TODO: Use composition and make a Note a member of NoteBlock
                note = Note(
                    x,
                    y,
                    block.ins,
                    block.key,
                    block.vel,
                    block.pan,
                    block.pit,
                )
                yield note

    @QtCore.pyqtSlot()
    def loadSelection(self, notes: List[Note]) -> None:
        for note in notes:
            block = self.addBlock(
                note.tick,
                note.layer,
                note.key,
                note.instrument,
                note.velocity,
                note.panning,
                note.pitch,
            )
            block.setSelected(True)
        self.updateBlockCount()
        self.updateSelectionStatus()
        self.selectionChanged.emit(self.selectionStatus)

    @QtCore.pyqtSlot()
    def copySelection(self):
        self.selectionCopied.emit(list(self.getSelectionData()))

    @QtCore.pyqtSlot()
    def cutSelection(self):
        self.copySelection()
        self.deleteSelection()

    @QtCore.pyqtSlot(list)
    def pasteSelection(self, notes: List[Note]):
        self.deselectAll()
        self.loadSelection(notes)
        self.retrieveSelection()

    def retrieveSelection(self):
        # If the mouse cursor is over the scene, move the selection to the cursor.
        # Otherwise, move the selection to the top left corner of the view.
        cursorPosition = self.view.mapFromGlobal(QtGui.QCursor.pos())

        if self.isClosingMenu:
            selectionPos = self.menuClickPos
            self.isClosingMenu = False
        elif self.view.viewport().geometry().contains(cursorPosition):
            selectionPos = cursorPosition
        else:
            viewTopLeftCorner = self.view.mapToScene(BLOCK_SIZE - 1, BLOCK_SIZE - 1)
            selectionPos = viewTopLeftCorner

        self.setSelectionTopLeft(selectionPos)

    ########## LAYERS ##########

    @QtCore.pyqtSlot(int)
    def setMinimumLayerCount(self, count: int) -> None:
        """
        Set the minimum number of layers that will be visible
        on the screen.
        """
        print("minimumLayerCount changed:", self.minimumLayerCount)
        if count != self.minimumLayerCount:
            self.minimumLayerCount = count
            self.updateSceneSize()

    def updateBlocksSelectableStatus(
        self, blocks: Optional[Sequence[NoteBlock]] = None
    ) -> None:
        """
        Update the selectable status of all note blocks in the scene according to
        their layer's lock status. If `blocks` is given and not empty, only those
        blocks will be updated.
        """
        # TODO: This might become a costly operation with a lot of note blocks on the scene.
        # Perhaps update it on addBlock, deselectAll etc. (only where new blocks may be placed under a locked layer)
        if not blocks:
            blocks = self.items()

        for block in blocks:
            layer = block.y() // BLOCK_SIZE
            if self.layers[layer].lock:
                block.setSelectable(True)
            else:
                block.setSelectable(False)

    def getLayerRegion(self, id: int) -> QtCore.QRectF:
        y1 = id * BLOCK_SIZE
        y2 = BLOCK_SIZE
        region = QtCore.QRectF(0, y1, self.width(), y2)
        return region

    def getRegionBelowLayer(self, id: int) -> QtCore.QRectF:
        yy = id * BLOCK_SIZE
        region = QtCore.QRectF(QtCore.QPointF(0, yy), self.sceneRect().bottomRight())
        return region

    def getBlocksInLayer(self, id: int) -> List[NoteBlock]:
        layerRegion = self.getLayerRegion(id)
        blocks = self.items(layerRegion)
        return blocks

    def getBlocksBelowLayer(self, id: int) -> List[NoteBlock]:
        region = self.getRegionBelowLayer(id)
        blocks = self.items(region)
        return blocks

    @QtCore.pyqtSlot(int, bool)
    def setLayerLock(self, id: int, lock: bool) -> None:
        # self.updateBlocksSelectableStatus()
        for block in self.getBlocksInLayer(id):
            block.setFlag(
                QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, not lock
            )
        self.update()

    @QtCore.pyqtSlot(int, bool)
    def setLayerSolo(self, id: int, solo: bool):
        self.update()

    @QtCore.pyqtSlot(int)
    def addLayer(self, id: int):
        blocksToShift = self.getBlocksBelowLayer(id)
        for block in blocksToShift:
            self._doMoveBlock(block, 0, 1)
        self.updateSceneSize()

    @QtCore.pyqtSlot(int)
    def removeLayer(self, id: int):
        for block in self.getBlocksInLayer(id):
            self.removeBlock(block)
        blocksToShift = self.getBlocksBelowLayer(id)
        for block in blocksToShift:
            self._doMoveBlock(block, 0, -1)
        self.updateSceneSize()

    @QtCore.pyqtSlot(int)
    def selectAllInLayer(self, id: int, clearPrevious: bool = True):
        if clearPrevious:
            self.deselectAll()
        self.setAreaSelected(self.getLayerRegion(id))

    @QtCore.pyqtSlot(int, int)
    def swapLayers(self, id1: int, id2: int):
        id1, id2 = min(id1, id2), max(id1, id2)

        blocks1 = self.getBlocksInLayer(id1)
        blocks2 = self.getBlocksInLayer(id2)

        origin1 = self.getLayerRegion(id1).topLeft().y()
        origin2 = self.getLayerRegion(id2).topLeft().y()
        distance = int(abs(origin2 - origin1) // BLOCK_SIZE)

        for block in blocks1:
            self._doMoveBlock(block, 0, distance)
        for block in blocks2:
            self._doMoveBlock(block, 0, distance)

    ########## PLAYBACK ##########

    def initPlayback(self):
        self.glowTimer = QtCore.QTimer(self)
        self.glowTimer.setInterval(1000 // 60)
        self.glowTimer.timeout.connect(self.updateBlockGlowEffect)
        self.glowTimer.start()

    @QtCore.pyqtSlot(float)
    def doPlayback(self, currentPlaybackPosition: float):
        if math.floor(self.previousPlaybackPosition) != math.floor(
            currentPlaybackPosition
        ):
            self.playTick(math.floor(currentPlaybackPosition))
        self.previousPlaybackPosition = currentPlaybackPosition
        self.updateBlockGlowEffect()

    def getBlocksInTick(self, tick: int) -> List[NoteBlock]:
        return self.tickIndex.get(tick) or []

    def playBlocks(self, blocks: Sequence[NoteBlock]) -> None:
        payload = []
        for block in blocks:
            layer = self.layers[int(block.y() // BLOCK_SIZE)]
            instrument = block.ins
            key = block.key + block.pit / 100
            volume = (block.vel / 100) * (layer.volume / 100)
            if layer.panning == 0:
                panning = block.pan / 100
            else:
                panning = ((block.pan / 100) * (layer.panning / 100)) / 2
            block.play()
            payload.append((instrument, key, volume, panning))
        self.playingBlocks.update(blocks)
        self.tickPlayed.emit(payload)

    def playTick(self, tick: int) -> None:
        blocks = self.getBlocksInTick(tick)
        if blocks:
            self.playBlocks(blocks)

    def updateBlockGlowEffect(self) -> None:
        toBeRemoved = set()
        for block in self.playingBlocks:
            block.updateGlow()
            if block.glow <= 0:
                toBeRemoved.add(block)
        self.playingBlocks -= toBeRemoved

    ########## EVENTS ##########

    def timerEvent(self, event):
        # Auto-scroll when dragging/moving near the edges
        hsb = self.view.horizontalScrollBar()
        vsb = self.view.verticalScrollBar()
        hsb.setValue(hsb.value() + self.scrollSpeedX)
        vsb.setValue(vsb.value() + self.scrollSpeedY)

    def mousePressEvent(self, event):
        self.selectionStart = event.scenePos()
        if event.button() == QtCore.Qt.RightButton:
            self.selection.setStyleSheet("selection-background-color: rgb(255, 0, 0);")
        elif event.button() == QtCore.Qt.LeftButton:
            clickedItem = self.itemAt(event.scenePos(), QtGui.QTransform())
            if clickedItem is not None and clickedItem.isSelected():
                self.isMovingBlocks = True
                self.movedItem = clickedItem
            else:
                if (
                    not QtGui.QGuiApplication.keyboardModifiers()
                    == QtCore.Qt.ControlModifier
                ):
                    self.deselectAllManual()
                self.selection.setStyleSheet("")
        self.selection.show()

    def mouseReleaseEvent(self, event):
        self.isRemovingNote = False
        self.scrollSpeedX = 0
        self.scrollSpeedY = 0
        if self.isDraggingSelection:
            selectionArea = self.view.mapToScene(
                self.selection.geometry()
            ).boundingRect()
            # TODO: Update selection as the selection box is dragged
            if event.button() == QtCore.Qt.LeftButton:
                self.setAreaSelected(selectionArea, True)
            elif event.button() == QtCore.Qt.RightButton:
                self.setAreaSelected(selectionArea, False)
            self.selection.hide()
            self.selection.setGeometry(0, 0, 0, 0)
            self.isDraggingSelection = False
        elif self.isClearingSelection:
            self.isClearingSelection = False
        elif self.isMovingBlocks:
            self.isMovingBlocks = False
        else:
            clickPos = event.scenePos()
            x, y = (round(i) for i in self.getGridPos(clickPos))
            if event.button() == QtCore.Qt.LeftButton:
                self.removeBlockManual(x, y)
                self.addBlockManual(
                    x, y, self.activeKey, self.currentInstrument, 100, 0, 0
                )
            elif event.button() == QtCore.Qt.RightButton:
                if not self.hasSelection():  # Should open the menu otherwise
                    if self.blockAtPos(event.pos()) is not None:
                        self.removeBlockManual(x, y)
                        self.isRemovingNote = True

    def mouseMoveEvent(self, event):
        # Auto-scroll when dragging/moving near the edges
        # TODO: Scroll speed slows down as you move the mouse outside the scene.
        # It should be capped at the max speed instead
        if (
            event.buttons() == QtCore.Qt.LeftButton
            or event.buttons() == QtCore.Qt.RightButton
        ):
            rect = self.view.rect()
            pos = self.view.mapFromScene(event.scenePos())
            if pos.x() < rect.center().x():
                self.scrollSpeedX = max(0, 50 - abs(rect.left() - pos.x())) * -1
            else:
                self.scrollSpeedX = max(0, 50 - abs(rect.right() - pos.x()))
            if pos.y() < rect.center().y():
                self.scrollSpeedY = max(0, 50 - abs(rect.top() - pos.y())) * -1
            else:
                self.scrollSpeedY = max(0, 50 - abs(rect.bottom() - pos.y()))
        if self.isMovingBlocks and event.buttons() == QtCore.Qt.LeftButton:
            pos = event.scenePos()
            x = (pos.x() // BLOCK_SIZE) * BLOCK_SIZE
            y = (pos.y() // BLOCK_SIZE) * BLOCK_SIZE
            origx = self.movedItem.x()
            origy = self.movedItem.y()
            dx = x - origx
            dy = y - origy
            movex = dx
            movey = dy
            if any(item.x() + dx < 0 for item in self.selectedItems()):
                movex = 0
            if any(item.y() + dy < 0 for item in self.selectedItems()):
                movey = 0
            for item in self.selectedItems():
                self._doMoveBlock(
                    item, int(movex // BLOCK_SIZE), int(movey // BLOCK_SIZE)
                )
        elif (
            event.buttons() == QtCore.Qt.LeftButton
            or event.buttons() == QtCore.Qt.RightButton
        ):
            self.isDraggingSelection = True
            selectionRect = QtCore.QRectF(self.selectionStart, event.scenePos())
            selectionRect = self.view.mapFromScene(selectionRect).boundingRect()
            self.selection.setGeometry(selectionRect)
        else:
            # call the parent's mouseMoveEvent to allow
            # the scene items to detect hover events
            super().mouseMoveEvent(event)
            self.selection.hide()

    def eventFilter(self, object: QtCore.QObject, event: QtCore.QEvent) -> bool:
        # Prevent right-clicking to delete a note from opening the menu
        if event.type() == QtCore.QEvent.GraphicsSceneContextMenu:
            if self.isRemovingNote:
                return True

        # Prevent left-clicking to close the menu from triggering a click on the scene
        elif (
            event.type() == QtCore.QEvent.GraphicsSceneMousePress
            or event.type() == QtCore.QEvent.GraphicsSceneMouseRelease
            or event.type() == QtCore.QEvent.GraphicsSceneMouseMove
        ):
            if event.button() == QtCore.Qt.LeftButton:
                if self.isClosingMenu:
                    if event.type() == QtCore.QEvent.GraphicsSceneMouseRelease:
                        self.isClosingMenu = False
                    return True

        return False


class NoteBlock(QtWidgets.QGraphicsItem):

    # Geometry
    RECT = QtCore.QRectF(0, 0, BLOCK_SIZE, BLOCK_SIZE)
    TOP_RECT = QtCore.QRect(0, 0, BLOCK_SIZE, BLOCK_SIZE // 2)
    BOTTOM_RECT = QtCore.QRect(0, BLOCK_SIZE // 2, BLOCK_SIZE, BLOCK_SIZE // 2)

    # Colors
    LABEL_COLOR = QtCore.Qt.yellow
    NUMBER_COLOR = QtCore.Qt.white

    # Font
    FONT = QtGui.QFont()
    FONT.setPointSize(9)

    def __init__(self, xx, yy, key, ins, vel=100, pan=0, pit=0, parent=None):
        super().__init__(parent)
        self.xx = xx
        self.yy = yy
        self.key = key
        self.ins = ins
        self.ins = min(ins, 15)
        self.vel = vel
        self.pan = pan
        self.pit = pit
        self.overlayColor = QtGui.QColor(*instrument_data[min(ins, 15)].color)
        self.overlayColor = QtGui.QColor(*instrument_data[min(ins, 15)].color)
        self.label = self.getLabel()
        self.clicks = self.getClicks()
        self.isOutOfRange = False
        self.selected = False
        self.setAcceptHoverEvents(True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        # TODO: ItemCoordinateCache makes items pixelated. Invalidate the cache
        # when zooming very close as few notes are being drawn.
        self.setCacheMode(QtWidgets.QGraphicsItem.ItemCoordinateCache)

        # OPACITY CONTROLS
        self.opacityEffect = QtWidgets.QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacityEffect)
        self.baseOpacity = 0.6
        self.glow = 0.0
        self.updateOpacity()

    @property
    def tick(self) -> int:
        return int(self.x() // BLOCK_SIZE)

    @property
    def layer(self) -> int:
        return int(self.y() // BLOCK_SIZE)

    def boundingRect(self):
        return self.RECT

    def updateOpacity(self):
        opacity = self.baseOpacity + self.glow * 0.4
        self.opacityEffect.setOpacity(opacity)

    def paint(self, painter, option, widget):
        pixmap = PIXMAP_CACHE.find(self.cacheKey)
        if pixmap is None:
            pixmap = self.getPixmap()
            PIXMAP_CACHE.insert(self.cacheKey, pixmap)
        painter.drawPixmap(0, 0, pixmap)

        selectedColor = QtGui.QColor(255, 255, 255, 180)
        if self.isSelected():
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(selectedColor)
            painter.drawRect(self.RECT)

    def getPixmap(self) -> QtGui.QPixmap:
        pixmap = QtGui.QPixmap(BLOCK_SIZE, BLOCK_SIZE)
        painter = QtGui.QPainter(pixmap)

        rect = self.RECT.toAlignedRect()
        painter.drawPixmap(rect, NOTE_BLOCK_PIXMAP)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QBrush(self.overlayColor, QtCore.Qt.SolidPattern))
        painter.setCompositionMode(QtGui.QPainter.CompositionMode_Overlay)
        painter.drawRect(rect)
        painter.setCompositionMode(QtGui.QPainter.CompositionMode_SourceOver)
        painter.setFont(self.FONT)
        painter.setPen(self.LABEL_COLOR)
        painter.drawText(
            self.TOP_RECT, QtCore.Qt.AlignHCenter + QtCore.Qt.AlignBottom, self.label
        )
        painter.setPen(self.NUMBER_COLOR)
        painter.drawText(
            self.BOTTOM_RECT, QtCore.Qt.AlignHCenter + QtCore.Qt.AlignTop, self.clicks
        )
        if self.isOutOfRange:
            painter.setPen(QtCore.Qt.red)
            painter.setBrush(QtCore.Qt.NoBrush)
            painter.drawRect(rect)

        painter.end()
        return pixmap

    def resetCache(self):
        PIXMAP_CACHE.remove(self.cacheKey)

    @property
    def cacheKey(self) -> str:
        return f"note_{self.ins}_{self.key}"

    def hoverEnterEvent(self, event):
        self.baseOpacity = 1.0
        self.updateOpacity()

    def hoverLeaveEvent(self, event):
        self.baseOpacity = 0.6
        self.updateOpacity()

    def wheelEvent(self, event):
        if event.delta() > 0:
            self.changeKey(1)
        else:
            self.changeKey(-1)

    def setSelectable(self, selectable: bool = True) -> None:
        self.setFlag(
            QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, selectable
        )

    def changeKey(self, steps):
        self.key += steps
        self.refresh()

    def refresh(self):
        self.label = self.getLabel()
        self.clicks = self.getClicks()
        self.update()

    def getLabel(self):
        octave, key = divmod(self.key + 9, 12)
        label = KEY_LABELS[key] + str(octave)
        return label

    def getClicks(self):
        # TODO: replace hardcoded values with the note instrument's valid range
        if self.key < 33:
            return "<"
        elif self.key > 57:
            return ">"
        else:
            return str(self.key - 33)

    def updateGlow(self):
        if self.glow >= 0:
            self.updateOpacity()
        self.glow -= 0.01

    def play(self):
        self.glow = 1
        self.updateOpacity()

    def getData(self):
        return (
            self.key,
            self.ins,
            self.vel,
            self.pan,
            self.pit,
        )

    def setInstrument(self, id_: int):
        self.ins = id_
        instrument = instrument_data[id_]
        self.overlayColor = QtGui.QColor(*instrument.color)
        self.update()
