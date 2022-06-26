from __future__ import annotations

import math
import pickle
from dataclasses import dataclass
from enum import Enum
from typing import Generator, List, Optional, Sequence, Tuple, Union

from nbs.core.context import appctxt
from nbs.core.data import Instrument, default_instruments
from nbs.core.utils import *
from nbs.ui.actions import Actions  # TODO: remove dependency
from nbs.ui.menus import EditMenu  # TODO: remove dependency
from PyQt5 import QtCore, QtGui, QtWidgets

from .constants import *

__all__ = ["NoteBlockArea"]


instrument_data = default_instruments  # TODO: replace with actual data


class TimeRuler(QtWidgets.QWidget):

    clicked = QtCore.pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(32)
        self.offset = 0
        self.scale = 1
        self.tempo = 10.00

    def getTextRect(self, fm: QtGui.QFontMetrics, text, x=0, y=0):
        # Calling boundingRect just once returns a wrong size. See:
        # https://stackoverflow.com/a/32078341/9045426
        textRect = fm.boundingRect(text)
        textRect = fm.boundingRect(textRect, 0, text)
        textRect.moveCenter(QtCore.QPoint(x, y))
        # if textRect.left() < 0 and textRect.right() >= (textRect.width() / 2):
        #    textRect.moveLeft(1)
        # if textRect.right() > rect.width():
        #    textRect.moveRight(textRect.width() - 1)
        return textRect

    def paintEvent(self, event):
        self.resize(self.parent().width(), self.height())
        rect = self.rect()
        mid = rect.height() / 2
        blocksize = BLOCK_SIZE * self.scale
        painter = QtGui.QPainter()
        painter.begin(self)
        fm = painter.fontMetrics()
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtCore.Qt.white)
        painter.drawRect(rect)
        painter.setPen(QtCore.Qt.black)
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
                    textRect, QtCore.Qt.AlignHCenter + QtCore.Qt.AlignTop, text
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
                textRect, QtCore.Qt.AlignHCenter + QtCore.Qt.AlignTop, text
            )
        painter.end()

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
        self.update()

    @QtCore.pyqtSlot(float)
    def setTempo(self, newTempo: float):
        self.tempo = newTempo
        self.update()


class Marker(QtWidgets.QWidget):

    moved = QtCore.pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pos = 0
        self.offset = 0
        self.scale = 1
        self.setMouseTracking(True)
        self.setCursor(QtCore.Qt.SizeHorCursor)
        self.setFixedHeight(800)
        self.setFixedWidth(16)
        self.raise_()

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        markerColor = QtCore.Qt.green
        pen = QtGui.QPen(markerColor)
        pen.setWidth(2)
        painter.setPen(pen)
        # pos = self.tickToPos(self.markerPos)
        # painter.drawLine(pos, 0, pos, self.height())
        painter.drawLine(8, 0, 8, self.height())
        painter.fillPath(self.getMarkerHead(), QtGui.QBrush(markerColor))
        painter.end()

    def getMarkerHead(self):
        point1 = QtCore.QPoint(0, 0)
        point2 = QtCore.QPoint(16, 0)
        point3 = QtCore.QPoint(8, 16)
        shape = QtGui.QPolygon([point1, point2, point3])
        region = QtGui.QRegion(shape)
        path = QtGui.QPainterPath()
        path.addRegion(region)
        return path

    def mouseMoveEvent(self, event):
        # The event pos is relative to the bounding box of the widget, so we calculate
        # how much it should move based on how far from the center the mouse moved
        if event.buttons() == QtCore.Qt.LeftButton:
            offset = event.pos().x() - 8
            pos = self.posToTick(self.tickToPos(self.pos) + offset)
            self.setPos(pos)
            self.moved.emit(pos)
        return

    def posToTick(self, pos):
        return (pos + self.offset) / (self.scale * BLOCK_SIZE)

    def tickToPos(self, tick):
        return tick * self.scale * BLOCK_SIZE - self.offset

    def updatePos(self):
        self.move(self.tickToPos(self.pos) - 8, 0)

    @QtCore.pyqtSlot(float)
    def setPos(self, pos: float):
        """Set the position of the marker, in ticks."""
        self.pos = max(0, pos)
        self.updatePos()

    @QtCore.pyqtSlot(int)
    def setOffset(self, value):
        self.offset = value
        self.updatePos()

    @QtCore.pyqtSlot(float)
    def setScale(self, value):
        self.scale = value
        self.updatePos()


@dataclass
class Layer:
    """Represents a layer in the note block area."""

    lock: bool = False
    solo: bool = False
    volume: int = 100
    panning: int = 0


class ScrollMode(Enum):
    """Enum for the different scroll modes for `NoteBlockView`."""

    NONE = 0
    PAGE_BY_PAGE = 1
    TICK_BY_TICK = 2


class NoteBlockView(QtWidgets.QGraphicsView):

    scaleChanged = QtCore.pyqtSignal(float)
    tempoChanged = QtCore.pyqtSignal(float)
    playbackPositionChanged = QtCore.pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent, objectName=__class__.__name__)
        self.currentScale = 1
        self.scrollMode = ScrollMode.PAGE_BY_PAGE
        self.ruler = TimeRuler(parent=self)
        self.marker = Marker(parent=self)

        self.setViewportMargins(0, 32, 0, 0)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.viewport().setObjectName(self.objectName() + "Viewport")
        self.viewport().installEventFilter(self)

        self.horizontalScrollBar().valueChanged.connect(self.ruler.setOffset)
        self.horizontalScrollBar().valueChanged.connect(self.marker.setOffset)
        self.scaleChanged.connect(self.ruler.setScale)
        self.scaleChanged.connect(self.marker.setScale)

        self.ruler.clicked.connect(self.playbackPositionChanged)
        self.marker.moved.connect(self.playbackPositionChanged)

        self.tempoChanged.connect(self.ruler.setTempo)

    @QtCore.pyqtSlot(float)
    def setPlaybackPosition(self, tick):
        self.marker.setPos(tick)
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
        if event.modifiers() == QtCore.Qt.ControlModifier:
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
        viewYCenter = (
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
    playbackPositionChanged = QtCore.pyqtSignal(int)

    ########## Public slots ##########
    selectionChanged = QtCore.pyqtSignal(int)
    clipboardChanged = QtCore.pyqtSignal()
    blockCountChanged = QtCore.pyqtSignal(int)
    blockAdded = QtCore.pyqtSignal(int, int, int, int, int)
    tickPlayed = QtCore.pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent, objectName=__class__.__name__)
        self.view = NoteBlockView(self)
        self.layers = []
        self.selection = QtWidgets.QRubberBand(
            QtWidgets.QRubberBand.Rectangle, parent=self.view.viewport()
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
        self.initUI()
        self.initClipboard()
        self.initPlayback()

    ########## UI ##########

    def initUI(self):
        self.updateSceneSize()
        self.installEventFilter(self)
        self.initMenu()
        self.view.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.view.setCursor(QtCore.Qt.PointingHandCursor)
        self.startTimer(10)

    def drawBackground(self, painter, rect):
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QColor(240, 240, 240))
        painter.drawRect(rect)
        painter.setPen(QtCore.Qt.SolidLine)
        start = int(rect.x() // BLOCK_SIZE)
        end = int(rect.right() // BLOCK_SIZE + 1)
        for x in range(start, end):
            if x % 4 == 0:
                painter.setPen(QtGui.QColor(181, 181, 181))
            else:
                painter.setPen(QtGui.QColor(216, 216, 216))
            painter.drawLine(x * BLOCK_SIZE, rect.y(), x * BLOCK_SIZE, rect.bottom())

    def drawForeground(self, painter: QtGui.QPainter, rect: QtCore.QRectF) -> None:
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtCore.Qt.black)
        painter.setOpacity(0.25)
        for id, layer in enumerate(self.layers):
            if layer.lock:
                painter.drawRect(self.getLayerRegion(id))

    ########## MENU ##########

    def initMenu(self):
        self.menu = EditMenu(self.view, isFloat=True)
        # Dismissing a menu should "cancel" the next click, but triggering an option should not.
        self.menu.aboutToHide.connect(self.onDismissMenu)
        self.menu.triggered.connect(self.onTriggerMenu)

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent) -> None:
        self.menuClickPos = event.scenePos()
        self.toggleSelectLeftRightActions(event.scenePos())
        self.menu.exec(event.screenPos())
        return super().contextMenuEvent(event)

    @QtCore.pyqtSlot()
    def onDismissMenu(self):
        self.isClosingMenu = True

    def onTriggerMenu(self):
        self.isClosingMenu = False

    def toggleSelectLeftRightActions(self, pos: Union[QtCore.QPoint, QtCore.QPointF]):
        bbox = self.itemsBoundingRect()

        if pos.x() < bbox.left():
            Actions.selectAllLeftAction.setEnabled(False)
        else:
            Actions.selectAllLeftAction.setEnabled(True)

        if pos.x() > bbox.right():
            Actions.selectAllRightAction.setEnabled(False)
        else:
            Actions.selectAllRightAction.setEnabled(True)

    ########## SLOTS ##########

    @QtCore.pyqtSlot(int)
    def setActiveKey(self, key):
        self.activeKey = key

    @QtCore.pyqtSlot(float)
    def setTempo(self, tempo):
        self.tempo = tempo

    ########## COORDINATE TRANSFORMATION ##########

    def updateSceneSize(self):
        if len(self.items()) > 1:
            bbox = self.itemsBoundingRect()
        else:
            bbox = QtCore.QRectF(0, 0, 0, 0)
        viewSize = self.view.rect()
        newSize = (
            math.ceil((bbox.right() + viewSize.width()) / BLOCK_SIZE) * BLOCK_SIZE,
            math.ceil((bbox.bottom() + viewSize.height()) / BLOCK_SIZE) * BLOCK_SIZE,
        )
        self.setSceneRect(QtCore.QRectF(0, 0, *newSize))
        self.updateLayerCount()
        self.sceneSizeChanged.emit(*newSize)
        print(*newSize)

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

    def getScenePos(self, x, y):
        """Return the top left scene position of a set of grid coordinates."""
        return QtCore.QPoint(x * BLOCK_SIZE, y * BLOCK_SIZE)

    def blockAtPos(self, pos: Union[QtCore.QPoint, QtCore.QPointF]):
        viewPos = self.view.mapFromScene(pos)
        viewTransform = self.view.transform()
        return self.itemAt(viewPos, viewTransform)

    ########## SONG ##########

    def reset(self) -> None:
        self.layers = []
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

    ########## NOTE BLOCKS ##########

    def clear(self):
        """Clear all note blocks in the scene."""
        for item in self.items():
            self.removeItem(item)

    def addBlock(self, x, y, *args, **kwargs):
        """Add a note block at the specified position."""
        blockPos = self.getScenePos(x, y)
        block = NoteBlock(x, y, *args, **kwargs)
        block.setPos(blockPos)
        self.addItem(block)
        return block

    def addBlockManual(self, x, y, *args, **kwargs):
        block = self.addBlock(x, y, *args, **kwargs)
        self.updateBlockCount()
        self.updateSceneSize()
        self.blockAdded.emit(block.ins, block.key, block.vel, block.pan, block.pit)

    def removeBlock(self, block: NoteBlock) -> None:
        self.removeItem(block)
        self.updateBlockCount()
        # TODO: self.blockRemoved.emit()

    def removeBlockAt(self, x, y):
        """Remove the note block at the specified position."""
        pos = self.getScenePos(x, y)
        clicked = self.itemAt(pos, QtGui.QTransform())
        if isinstance(clicked, NoteBlock):
            self.removeBlock(clicked)

    def removeBlockManual(self, x, y):
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
            block.moveBy(x * BLOCK_SIZE, y * BLOCK_SIZE)

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
            relativePosX = block.x() - origin.x()
            block.moveBy(relativePosX, 0)

    def compressSelection(self):
        bbox = self.selectionBoundingRect()
        origin = bbox.topLeft()

        for block in self.selectedItems():
            relativePosX = block.x() - origin.x()
            distance = (-relativePosX / 2) // BLOCK_SIZE * BLOCK_SIZE
            block.moveBy(distance, 0)

        for block in self.selectedItems():
            while block.collidingItems():
                block.moveBy(0, BLOCK_SIZE)

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

    def getSelectionData(self) -> Generator[Tuple[int, ...], None, None]:
        origin = self.selectionBoundingRect().topLeft()
        for block in self.selectedItems():
            if isinstance(block, NoteBlock):
                x = (block.x() - origin.x()) // BLOCK_SIZE
                y = (block.y() - origin.y()) // BLOCK_SIZE
                data = (x, y, *block.getData())
                yield data

    def getSelectionDataAsList(self) -> List[Tuple[int, ...]]:
        return list(self.getSelectionData())

    def getSelectionMimeData(self) -> QtCore.QMimeData:
        mimeData = QtCore.QMimeData()
        mimeData.setData(
            "application/nbs-noteblock-selection",
            QtCore.QByteArray(pickle.dumps(self.getSelectionDataAsList())),
        )
        return mimeData

    def loadSelectionMimeData(self, mimeData: QtCore.QMimeData):
        if mimeData.hasFormat("application/nbs-noteblock-selection"):
            data = pickle.loads(mimeData.data("application/nbs-noteblock-selection"))
            for x, y, *data in data:
                block = self.addBlock(x, y, *data)
                block.setSelected(True)
            self.updateBlockCount()
            self.updateSelectionStatus()
            self.selectionChanged.emit(self.selectionStatus)

    def initClipboard(self):
        self.clipboard = QtWidgets.QApplication.clipboard()
        self.clipboard.dataChanged.connect(self.clipboardChanged)

    @QtCore.pyqtSlot()
    def copySelection(self):
        self.clipboard.setMimeData(self.getSelectionMimeData())

    @QtCore.pyqtSlot()
    def cutSelection(self):
        self.copySelection()
        self.deleteSelection()

    @QtCore.pyqtSlot()
    def pasteSelection(self):
        self.deselectAll()
        self.loadSelectionMimeData(self.clipboard.mimeData())
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

    def updateLayerCount(self):
        layerCount = self.height() // BLOCK_SIZE
        while len(self.layers) < layerCount:
            self.layers.append(Layer())
        while len(self.layers) > layerCount:
            self.layers.pop()
        print("New layer count:", len(self.layers))

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
        print(0, y1, self.width(), y2)
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

    @QtCore.pyqtSlot(int, int)
    def setLayerVolume(self, id: int, volume: int):
        self.layers[id].volume = volume

    @QtCore.pyqtSlot(int, int)
    def setLayerPanning(self, id: int, panning: int):
        self.layers[id].panning = panning

    @QtCore.pyqtSlot(int, bool)
    def setLayerLock(self, id: int, lock: bool):
        self.layers[id].lock = lock
        for block in self.getBlocksInLayer(id):
            block.setFlag(
                QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, not lock
            )
        self.update()

    @QtCore.pyqtSlot(int, bool)
    def setLayerSolo(self, id: int, solo: bool):
        self.layers[id].solo = solo
        self.update()

    @QtCore.pyqtSlot(int)
    def addLayer(self, id: int):
        blocksToShift = self.getBlocksBelowLayer(id)
        for block in blocksToShift:
            block.moveBy(0, BLOCK_SIZE)

        self.layers.insert(id, Layer())

        self.updateSceneSize()

    @QtCore.pyqtSlot(int)
    def removeLayer(self, id: int):
        for block in self.getBlocksInLayer(id):
            self.removeBlock(block)
        blocksToShift = self.getBlocksBelowLayer(id)
        for block in blocksToShift:
            block.moveBy(0, -BLOCK_SIZE)

        self.layers.pop(id)

        self.updateSceneSize()

    @QtCore.pyqtSlot(int)
    def selectAllInLayer(self, id: int, clearPrevious: bool = True):
        if clearPrevious:
            self.deselectAll()
        self.setAreaSelected(self.getLayerRegion(id))

    def shiftLayers(self, id1: int, id2: int):
        blocks1 = self.getBlocksInLayer(id1)
        blocks2 = self.getBlocksInLayer(id2)

        origin1 = self.getLayerRegion(id1).topLeft().y()
        origin2 = self.getLayerRegion(id2).topLeft().y()
        distance = abs(origin2 - origin1)

        for block in blocks1:
            block.moveBy(0, distance)
        for block in blocks2:
            block.moveBy(0, -distance)

        tempLayer = self.layers[id1]
        self.layers[id1] = self.layers[id2]
        self.layers[id2] = tempLayer

    ########## PLAYBACK ##########

    def initPlayback(self):
        self.glowTimer = QtCore.QTimer(self)
        self.glowTimer.setInterval(1000 / 60)
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

    def getTickRegion(self, tick: int) -> QtCore.QRectF:
        x1 = tick * BLOCK_SIZE
        x2 = BLOCK_SIZE
        region = QtCore.QRectF(x1, 0, x2, self.sceneRect().height())
        return region

    def getBlocksInTick(self, tick: int) -> List[NoteBlock]:
        region = self.getTickRegion(tick)
        blocks = self.items(region)
        return blocks

    def playBlocks(self, blocks: Sequence[NoteBlock]) -> None:
        payload = []
        for block in blocks:
            layer = self.layers[int(block.y() // BLOCK_SIZE)]
            instrument = block.ins
            key = block.key
            volume = block.vel * layer.volume
            panning = (block.pan * layer.panning) / 2
            pitch = block.pit
            block.play()
            payload.append((instrument, key, volume, panning, pitch))
        self.playingBlocks.update(blocks)
        self.tickPlayed.emit(payload)

    def playTick(self, tick: int) -> None:
        blocks = self.getBlocksInTick(tick)
        self.playBlocks(blocks)

    def updateBlockGlowEffect(self) -> None:
        toBeRemoved = set()
        for block in self.playingBlocks:
            block.updateGlow()
            if block.glow < 0:
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
            x, y = self.getGridPos(clickPos)
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
                item.moveBy(movex, movey)
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
    TOP_RECT = QtCore.QRect(0, 0, BLOCK_SIZE, BLOCK_SIZE / 2)
    BOTTOM_RECT = QtCore.QRect(0, BLOCK_SIZE / 2, BLOCK_SIZE, BLOCK_SIZE / 2)

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
        self.overlayColor = QtGui.QColor(*instrument_data[ins].color)
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

        # DRAWING CACHE
        self.cachePixmap = QtGui.QPixmap()

    def boundingRect(self):
        return self.RECT

    def updateOpacity(self):
        opacity = self.baseOpacity + self.glow * 0.4
        self.opacityEffect.setOpacity(opacity)

    def paint(self, painter, option, widget):
        if self.cachePixmap.isNull():
            print("repainting")
            self.paintCache()
        else:
            print("drawing from cache")
        painter.drawPixmap(0, 0, self.cachePixmap)

        selectedColor = QtGui.QColor(255, 255, 255, 180)
        if self.isSelected():
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(selectedColor)
            painter.drawRect(self.RECT)

    def paintCache(self) -> None:
        self.cachePixmap = QtGui.QPixmap(BLOCK_SIZE, BLOCK_SIZE)
        painter = QtGui.QPainter(self.cachePixmap)

        # Turn this into a QGraphicsPixmapItem and use a single pixmap for all note blocks.
        pixmap = QtGui.QPixmap(appctxt.get_resource("images/note_block_grayscale.png"))
        rect = self.RECT.toAlignedRect()
        painter.drawPixmap(rect, pixmap)
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

    def resetCache(self):
        self.cachePixmap.swap(QtGui.QPixmap())

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

    def setSelectable(self, selectable: Optional[bool] = True) -> None:
        self.setFlag(
            QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, selectable
        )

    def changeKey(self, steps):
        self.key += steps
        self.refresh()

    def refresh(self):
        self.label = self.getLabel()
        self.clicks = self.getClicks()
        self.resetCache()
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
        if self.glow > 0:
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
        self.resetCache()
        self.update()
