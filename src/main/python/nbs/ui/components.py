from PyQt5 import QtCore, QtGui, QtWidgets
from fbs_runtime.application_context.PyQt5 import ApplicationContext
import qtawesome as qta
import math
from nbs.core.utils import *

appctxt = ApplicationContext()

SCROLL_BAR_SIZE = QtWidgets.qApp.style().pixelMetric(
    QtWidgets.QStyle.PM_ScrollBarExtent
)
BLOCK_SIZE = 32

KEY_LABELS = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")


class VerticalScrollArea(QtWidgets.QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup()

    def setup(self):
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Resize:
            obj.setMinimumWidth(self.minimumSizeHint().width() + 40)
        return super().eventFilter(obj, event)


class PianoKey(QtWidgets.QWidget):
    """
    A single piano key, which can be white or black.

    Arguments:
        num (int): the number of this key within the parent PianoWidget
        label (str): the label that will appear on this key
        isBlack (bool): whether this key is black or white (default False)
        isOutOfRange (bool): whether this key is outside the valid range (default False)

    Attributes:

    """

    keyPressed = QtCore.pyqtSignal(int)
    keyReleased = QtCore.pyqtSignal(int)

    def __init__(self, num, label="", isBlack=False, isOutOfRange=False, parent=None):
        super().__init__(parent)
        self.num = num
        self.label = label
        self.isBlack = isBlack
        self.isOutOfRange = isOutOfRange
        self.isPressed = False
        self.isActive = False
        self.previousKey = None
        self.currentKey = None
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.installEventFilter(self)

    def pressKey(self):
        if not self.isPressed:
            print("Pressed key", self.label)
            self.keyPressed.emit(self.num)
            self.isPressed = True
            self.update()

    def releaseKey(self):
        if self.isPressed:
            print("Released key", self.label)
            self.keyReleased.emit(self.num)
            self.isPressed = False
            self.update()

    def paintEvent(self, event):
        # Colors
        if self.isBlack:
            if self.isActive:
                color = QtGui.QColor(51, 102, 255)
            elif self.isOutOfRange:
                color = QtGui.QColor(61, 15, 15)
            else:
                color = QtGui.QColor(30, 30, 30)
            if self.isPressed:
                color = color.lighter(110)
            textColor = QtCore.Qt.white
        else:
            if self.isActive:
                color = QtGui.QColor(51, 102, 255)
            elif self.isOutOfRange:
                color = QtGui.QColor(234, 170, 168)
            else:
                color = QtGui.QColor(255, 255, 255)
            if self.isPressed:
                color = color.darker(120)
            textColor = QtCore.Qt.black
        bevelColor = color.darker(130)
        outlineColor = color.darker(200)

        # Geometry
        rect = self.rect()
        if self.isPressed:
            rect.translate(0, 10)
        bevel = self.rect()
        bevel.setHeight(12)
        bevel.moveBottom(rect.bottom())
        textRect = self.rect()
        textRect.setBottom(bevel.top() - 15)

        # Paint
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.fillRect(rect, color)
        painter.fillRect(bevel, bevelColor)
        pen = QtGui.QPen(outlineColor)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRects(rect, bevel)
        painter.setPen(textColor)
        painter.drawText(
            textRect, QtCore.Qt.AlignCenter + QtCore.Qt.AlignBottom, self.label
        )
        painter.end()

    def eventFilter(self, obj, event):
        # Since widgets happens to grab the mouse whenever you click one,
        # in order to allow sliding the mouse over the piano, we install
        # an eventFilter on every piano key to detect when the mouse moves
        # over a certain key, then tell that key to be pressed.
        if event.type() == QtCore.QEvent.MouseButtonPress:
            self.pressKey()
        if event.type() == QtCore.QEvent.MouseButtonRelease:
            self.releaseKey()
            if self.currentKey is not None:
                self.currentKey.releaseKey()
        if event.type() == QtCore.QEvent.MouseMove:
            moveEvent = QtGui.QMouseEvent(event)
            widget = QtWidgets.qApp.widgetAt(moveEvent.globalPos())
            self.currentKey = widget if isinstance(widget, PianoKey) else None
            if self.previousKey is not None and self.previousKey != self.currentKey:
                self.previousKey.releaseKey()
            if (
                self.currentKey is not None
                and moveEvent.buttons() == QtCore.Qt.LeftButton
            ):
                self.currentKey.pressKey()
            self.previousKey = self.currentKey
        return False


class PianoWidget(QtWidgets.QWidget):
    """
    Create a piano widget.

    Arguments:
        keyCount (int): number of keys
        offset (int): offset from C0 to apply to the first key
        validRange (int, int): a 2-tuple representing the interval (inclusive)
            in which keys will be considered in range

    Attributes:

    Methods:

    """

    activeKeyChanged = QtCore.pyqtSignal(int)

    def __init__(self, keyCount, offset, validRange=(), parent=None):
        super().__init__(parent)
        self.keyCount = keyCount
        self.offset = offset
        if not validRange:
            self._validRange = (0, self.keyCount)
        else:
            self._validRange = validRange
        self._activeKey = None
        self.initUI()

    @property
    def validRange(self):
        return self._validRange

    @validRange.setter
    def validRange(self, value):
        self._validRange = (min(value[0], 0), max(value[1], self.keyCount))
        self.repaint()

    @property
    def activeKey(self):
        return self._activeKey

    @activeKey.setter
    def activeKey(self, value):
        if self._activeKey is not None:
            self.keys[self._activeKey].isActive = False
        self.keys[value].isActive = True
        self._activeKey = value
        self.activeKeyChanged.emit(value)
        self.repaint()

    @QtCore.pyqtSlot(int)
    def setActiveKey(self, key):
        self.activeKey = key

    def initUI(self):
        self.keys = []
        self.whiteKeys = []
        self.blackKeys = []
        self.blackPositions = (1, 3, 6, 8, 10)
        self.layout = QtWidgets.QHBoxLayout()
        # Bigger margin on the top to accomodate raised black keys
        self.layout.setContentsMargins(10, 15, 10, 25)
        self.layout.setSpacing(2)

        for i in range(self.keyCount):
            rangeMin, rangeMax = self._validRange
            isOutOfRange = not (rangeMin <= i <= rangeMax)
            oct, key = divmod(i + self.offset, 12)
            label = KEY_LABELS[key] + str(oct)
            isBlack = key in self.blackPositions
            key = PianoKey(i, label, isBlack, isOutOfRange, parent=self)
            if isBlack:
                self.blackKeys.append(key)
            else:
                self.whiteKeys.append(key)
                self.layout.addWidget(key)
            key.keyPressed.connect(self.setActiveKey)
            self.keys.append(key)

        self.setLayout(self.layout)
        self.resize(2400, 160)  # TODO: hardcoded

    def blackKeysInRange(self, min, max):
        """Return the number of black keys in a given range."""
        count = 0
        for i in range(min, max):
            key = i % 12
            if key in self.blackPositions:
                count += 1
        return count

    def arrangeBlackKeys(self):
        """Update position of the black keys on the piano."""
        key = self.whiteKeys[0]
        keyWidth = key.width() / 1.6
        keyHeight = key.height() / 1.6
        keyOffset = key.width() / 1.5
        yPos = key.y() - 10
        offset = self.blackKeysInRange(0, self.offset)
        for i in range(len(self.blackKeys)):
            oct, key = divmod(i + offset, 5)
            pos = oct * 12 + self.blackPositions[key] - self.offset
            # Set x pos based on the position of the previous (white) key
            xPos = self.keys[pos - 1].x() + keyOffset
            self.blackKeys[i].resize(keyWidth, keyHeight)
            self.blackKeys[i].move(xPos, yPos)
            self.blackKeys[i].raise_()

    def resizeEvent(self, event):
        self.arrangeBlackKeys()


class PianoScroll(QtWidgets.QScrollArea):
    """
    A scrolling area containing a piano widget.
    Takes the same arguments as PianoWidget().
    """

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent)
        self.mouseNearLeftEdge = False
        self.mouseNearRightEdge = False
        self.piano = PianoWidget(*args, **kwargs)
        self.initUI()

    def initUI(self):
        self.setWidget(self.piano)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setMouseTracking(True)
        self.startTimer(10)

    def timerEvent(self, event):
        self.checkAutoScroll()

    def checkAutoScroll(self):
        sb = self.horizontalScrollBar()
        if self.mouseNearLeftEdge:
            sb.setValue(sb.value() - 5)
        elif self.mouseNearRightEdge:
            sb.setValue(sb.value() + 5)

    def mouseMoveEvent(self, event):
        """Allow scrolling the piano by placing the mouse near the edges."""
        leftEdge = self.rect()
        leftEdge.setRight(50)
        rightEdge = self.rect()
        rightEdge.setLeft(self.width() - 50)
        mousePos = event.pos()
        self.mouseNearLeftEdge = leftEdge.contains(mousePos)
        self.mouseNearRightEdge = rightEdge.contains(mousePos)


class SongTime(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.currentTime = 10

    def paintEvent(self, event):
        # TODO: this can probably be a QLabel
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setPen(QtCore.Qt.black)

        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        painter.setFont(font)

        height = self.height()
        midpoint = height / 2
        width = self.width()
        rect = QtCore.QRect(0, 0, width, midpoint)

        alignFlags = QtCore.Qt.AlignRight + QtCore.Qt.AlignTop

        painter.drawText(rect, alignFlags, "0:00;000")

        font.setPointSize(8)
        font.setBold(False)
        rect.translate(0, midpoint)

        painter.setFont(font)
        painter.drawText(rect, alignFlags, "/ 0:00;000")
        painter.end()


class TimeBar(QtWidgets.QWidget):

    tempoChanged = QtCore.pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(32)
        self.currentTime = 0
        self.totalTime = 100
        self.tempo = 10.0
        self.displayBpm = False
        self.initUI()

    def initUI(self):
        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setMaximumWidth(342)  # TODO: calculate instead of hardcode

        # Song time
        self.songTime = SongTime()
        self.layout.addWidget(self.songTime)

        # Tempo box
        self.tempoBox = QtWidgets.QDoubleSpinBox()
        self.tempoBox.setRange(0, 60)
        self.tempoBox.setSingleStep(0.25)
        self.tempoBox.setValue(self.tempo)
        self.tempoBox.valueChanged.connect(self.changeTempo)

        self.tempoUnit = QtWidgets.QPushButton()
        self.tempoUnit.setText("t/s")
        # self.tempoUnit.setSizePolicy(
        #    QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum
        # )
        self.tempoUnit.setFixedWidth(40)
        self.tempoUnit.setFixedHeight(20)
        self.tempoUnit.setToolTip(
            "Click to change the displayed tempo unit. This has no effect on the song."
        )
        self.tempoUnit.clicked.connect(self.tempoUnitButtonClicked)
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.tempoBox)
        layout.addWidget(self.tempoUnit)
        layout.setContentsMargins(0, 0, 0, 0)
        container = QtWidgets.QWidget()
        container.setLayout(layout)

        self.layout.addWidget(self.songTime)
        self.layout.addWidget(container)

    def changeTempo(self):
        newValue = self.tempoBox.value()
        if self.displayBpm:
            self.tempo = newValue / 15
        else:
            self.tempo = newValue
        self.tempoChanged.emit(self.tempo)

    @QtCore.pyqtSlot(float)
    def currentTimeChanged(self, newPosInTicks: float):
        self.currentTime = newPosInTicks

    @QtCore.pyqtSlot(float)
    def songLengthChanged(self, newSongLength: float):
        self.totalTime = newSongLength

    @QtCore.pyqtSlot()
    def tempoUnitButtonClicked(self):
        self.displayBpm = not self.displayBpm

        # TODO: move all this logic to a separate class, it's complicated enough that it needs its own widget!!
        if self.displayBpm:
            self.tempoUnit.setText("BPM")
            self.tempoBox.setRange(0, 60 * 15)
            self.tempoBox.setValue(self.tempoBox.value() * 15)
        else:
            self.tempoUnit.setText("t/s")
            self.tempoBox.setValue(self.tempoBox.value() / 15)
            self.tempoBox.setRange(0, 60)


class TimeRuler(QtWidgets.QWidget):

    clicked = QtCore.pyqtSignal(int)

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
        self.clicked.emit(pos)
        self.update()

    @QtCore.pyqtSlot(int)
    def setOffset(self, value):
        self.offset = value
        self.update()

    @QtCore.pyqtSlot(float)
    def setScale(self, value):
        self.scale = value
        self.update()


class Marker(QtWidgets.QWidget):
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
        self.move(25, 0)

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
            pos = self.tickToPos(self.pos) + offset
            self.setPos(pos)
        return

    def posToTick(self, pos):
        return (pos / (self.scale * BLOCK_SIZE)) + (self.offset / BLOCK_SIZE)

    def tickToPos(self, tick):
        # TODO: Fix click position being incorrect when the view is scaled. I'm really close here.
        return tick * self.scale * BLOCK_SIZE - self.offset

    def updatePos(self):
        print(self.pos, self.scale, self.offset)
        self.move(self.tickToPos(self.pos) - 8, 0)

    @QtCore.pyqtSlot(int)
    def setPos(self, pos):
        self.pos = max(0, self.posToTick(pos))
        self.updatePos()

    @QtCore.pyqtSlot(int)
    def setOffset(self, value):
        self.offset = value
        self.updatePos()

    @QtCore.pyqtSlot(float)
    def setScale(self, value):
        self.scale = value
        self.updatePos()


class NoteBlockView(QtWidgets.QGraphicsView):

    scaleChanged = QtCore.pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.currentScale = 1
        self.ruler = TimeRuler(parent=self)
        self.marker = Marker(parent=self)
        ########self.setStyleSheet("QGraphicsView { border-top: none; }")
        # self.horizontalScrollBar().setStyle(QtWidgets.qApp.style())
        self.setViewportMargins(0, BLOCK_SIZE, 0, 0)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        self.horizontalScrollBar().valueChanged.connect(self.ruler.setOffset)
        self.horizontalScrollBar().valueChanged.connect(self.marker.setOffset)
        self.scaleChanged.connect(self.ruler.setScale)
        self.scaleChanged.connect(self.marker.setScale)
        self.ruler.clicked.connect(self.scene().setMarkerPos)
        self.ruler.clicked.connect(self.marker.setPos)

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


class NoteBlockArea(QtWidgets.QGraphicsScene):
    """
    A scrolling area that holds the note blocks in a song.
    """

    sceneSizeChanged = QtCore.pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.view = NoteBlockView(self)
        self.selection = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle)
        self.selectionStart = None
        self.isDraggingSelection = False
        self.isClearingSelection = False
        self.isMovingBlocks = False
        self.scrollSpeedX = 0
        self.scrollSpeedY = 0
        self.activeKey = 45
        self.markerPos = 0
        self.initUI()

    def initUI(self):
        self.updateSceneSize()
        self.view.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.view.setCursor(QtCore.Qt.PointingHandCursor)
        self.view.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)
        self.selectionProxy = self.addWidget(self.selection)
        self.selectionProxy.setZValue(1)
        self.startTimer(10)

    def noteBlocks(self):
        """An iterator which yields all the note blocks in the scene."""
        for item in self.items():
            if isinstance(item, NoteBlock):
                yield item

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

    def timerEvent(self, event):
        # Auto-scroll when dragging/moving near the edges
        hsb = self.view.horizontalScrollBar()
        vsb = self.view.verticalScrollBar()
        hsb.setValue(hsb.value() + self.scrollSpeedX)
        vsb.setValue(vsb.value() + self.scrollSpeedY)

    @QtCore.pyqtSlot(int)
    def setActiveKey(self, key):
        self.activeKey = key

    @QtCore.pyqtSlot(int)
    def setMarkerPos(self, pos):
        scenePos = self.view.mapToScene(QtCore.QPoint(pos, 0)).x()
        self.markerPos = scenePos
        self.update()

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

    def clear(self):
        """Clear all note blocks in the scene."""
        for item in self.noteBlocks():
            self.removeItem(item)

    def addBlock(self, x, y, *args, **kwargs):
        """Add a note block at the specified position."""
        blockPos = self.getScenePos(x, y)
        block = NoteBlock(x, y, *args, **kwargs)
        block.setPos(blockPos)
        block.mouseOver = True
        self.addItem(block)

    def addBlockManual(self, x, y, *args, **kwargs):
        self.addBlock(x, y, *args, **kwargs)
        self.updateSceneSize()

    def removeBlock(self, x, y):
        """Remove the note block at the specified position."""
        pos = self.getScenePos(x, y)
        clicked = self.itemAt(pos, QtGui.QTransform())
        if isinstance(clicked, NoteBlock):
            self.removeItem(clicked)

    def removeBlockManual(self, x, y):
        self.removeBlock(x, y)
        self.updateSceneSize()

    def setSelected(self, area: QtCore.QRectF, value=True):
        for item in self.items(area):
            item.setSelected(value)
            item.setZValue(1 if value else 0)

    def clearSelection(self):
        if len(self.selectedItems()) > 0:
            # This is done to prevent the next mouse
            # release from adding a note block
            self.isClearingSelection = True
            for item in self.selectedItems():
                for i in item.collidingItems():
                    self.removeItem(i)
                item.setSelected(False)
                item.setZValue(0)
            self.updateSceneSize()

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
                    self.clearSelection()
                self.selection.setStyleSheet("")
        self.selection.show()

    def mouseReleaseEvent(self, event):
        self.scrollSpeedX = 0
        self.scrollSpeedY = 0
        if self.isDraggingSelection:
            selectionArea = QtCore.QRectF(self.selection.geometry())
            # TODO: Update selection as the selection box is dragged
            if event.button() == QtCore.Qt.LeftButton:
                self.setSelected(selectionArea, True)
            elif event.button() == QtCore.Qt.RightButton:
                self.setSelected(selectionArea, False)
            self.selection.hide()
            self.selection.setGeometry(QtCore.QRect(0, 0, 0, 0))
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
                self.addBlockManual(x, y, self.activeKey, 100, 0, 0)
            elif event.button() == QtCore.Qt.RightButton:
                self.removeBlockManual(x, y)

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
            selectionRect = (
                QtCore.QRectF(self.selectionStart, event.scenePos())
                .normalized()
                .toRect()
            )
            self.selection.setGeometry(selectionRect)
        else:
            # call the parent's mouseMoveEvent to allow
            # the scene items to detect hover events
            super().mouseMoveEvent(event)
            self.selection.hide()


class NoteBlock(QtWidgets.QGraphicsItem):
    def __init__(self, xx, yy, key, ins, vel=100, pan=0, pit=0, parent=None):
        super().__init__(parent)
        self.xx = xx
        self.yy = yy
        self.key = key
        self.ins = ins
        self.vel = vel
        self.pan = pan
        self.pit = pit
        self.label = self.getLabel()
        self.clicks = self.getClicks()
        self.isOutOfRange = False
        self.mouseOver = False
        self.selected = False
        self.setAcceptHoverEvents(True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        # TODO: experiment with other caching mores such as ItemCoordinateCache,
        # optimize drawing code by reducing detail when zoomed out far etc.
        self.setCacheMode(QtWidgets.QGraphicsItem.DeviceCoordinateCache)

    def boundingRect(self):
        return QtCore.QRectF(0, 0, BLOCK_SIZE, BLOCK_SIZE)

    def paint(self, painter, option, widget):
        # Geometry
        rect = self.boundingRect().toAlignedRect()
        midpoint = rect.height() / 2
        labelRect = self.boundingRect()
        labelRect.setBottom(midpoint)
        numberRect = self.boundingRect()
        numberRect.setTop(midpoint)

        # Colors
        blockColor = QtGui.QColor(60, 60, 255)  # replace with instrument color
        labelColor = QtCore.Qt.yellow
        numberColor = QtCore.Qt.white
        selectedColor = QtGui.QColor(255, 255, 255, 180)

        # Font
        font = QtGui.QFont()
        font.setPointSize(9)

        # Paint
        if self.mouseOver:
            painter.setOpacity(1)
        else:
            painter.setOpacity(0.75)

        pixmap = QtGui.QPixmap(appctxt.get_resource("images/note_block_grayscale.png"))
        painter.drawPixmap(rect, pixmap)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QBrush(blockColor, QtCore.Qt.SolidPattern))
        painter.setCompositionMode(QtGui.QPainter.CompositionMode_Overlay)
        painter.drawRect(rect)
        painter.setCompositionMode(QtGui.QPainter.CompositionMode_SourceOver)
        painter.setOpacity(1)
        painter.setFont(font)
        painter.setPen(labelColor)
        painter.drawText(
            labelRect, QtCore.Qt.AlignHCenter + QtCore.Qt.AlignBottom, self.label
        )
        painter.setPen(numberColor)
        painter.drawText(
            numberRect, QtCore.Qt.AlignHCenter + QtCore.Qt.AlignTop, self.clicks
        )
        if self.isSelected():
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(selectedColor)
            painter.drawRect(rect)
        if self.isOutOfRange:
            painter.setPen(QtCore.Qt.red)
            painter.setBrush(QtCore.Qt.NoBrush)
            painter.drawRect(rect)

    def hoverEnterEvent(self, event):
        self.mouseOver = True
        self.update()

    def hoverLeaveEvent(self, event):
        self.mouseOver = False
        self.update()

    def wheelEvent(self, event):
        if event.delta() > 0:
            self.changeKey(1)
        else:
            self.changeKey(-1)

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


class LayerBar(QtWidgets.QToolBar):
    """A single layer bar."""

    def __init__(
        self,
        num,
        height,
        name="",
        volume=100,
        panning=100,
        locked=False,
        solo=False,
        parent=None,
    ):
        super().__init__(parent)
        self.num = num
        self.name = name
        self.volume = volume
        self.panning = panning
        self.locked = locked
        self.solo = solo
        self.icons = self.initIcons()
        self.initUI(height)

    def initIcons(self):
        return {
            "volume": qta.icon("mdi.volume-high"),
            "stereo": qta.icon("mdi.equalizer"),
            "lock_locked": qta.icon("mdi.lock-outline"),
            "lock_unlocked": qta.icon("mdi.lock-open-variant-outline"),
            "solo": qta.icon("mdi.exclamation-thick"),
            "select_all": qta.icon("mdi.select-all"),
            "insert": qta.icon("mdi.plus-circle-outline"),  # mdi.plus-box
            "remove": qta.icon("mdi.delete-outline"),  # mdi.trash-can
            "shift_up": qta.icon("mdi.arrow-up-bold"),
            "shift_down": qta.icon("mdi.arrow-down-bold"),
        }

    def initUI(self, height):
        self.setIconSize(QtCore.QSize(20, 24))
        self.setFixedHeight(height - 2)
        self.setMaximumWidth(342)  # TODO: calculate instead of hardcode
        sizePolicy = self.sizePolicy()
        sizePolicy.setRetainSizeWhenHidden(True)
        self.setSizePolicy(sizePolicy)
        self.addFrame()
        self.addContents()

    def addFrame(self):
        self.layout = QtWidgets.QHBoxLayout()
        self.layout.setContentsMargins(5, 0, 5, 0)
        self.layout.addWidget(self)
        self.frame = QtWidgets.QFrame()
        self.frame.setFrameStyle(QtWidgets.QFrame.Panel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setLineWidth(1)
        self.frame.setLayout(self.layout)

    def addContents(self):
        self.nameBox = QtWidgets.QLineEdit()
        self.nameBox.setFixedSize(76, 16)
        self.nameBox.setPlaceholderText("Layer {}".format(self.num + 1))
        self.addWidget(self.nameBox)
        self.addAction(self.icons["volume"], "Volume")
        self.addAction(self.icons["stereo"], "Stereo panning")
        self.addAction(self.icons["lock_unlocked"], "Lock this layer")
        self.addAction(self.icons["solo"], "Solo this layer")
        self.addAction(self.icons["select_all"], "Select all note blocks in this layer")
        self.addAction(self.icons["insert"], "Add empty layer here")
        self.addAction(self.icons["remove"], "Remove this layer")
        self.addAction(self.icons["shift_up"], "Shift layer up")
        self.addAction(self.icons["shift_down"], "Shift layer down")

    @QtCore.pyqtSlot(float)
    def changeScale(self, factor):
        self.setFixedHeight(factor * BLOCK_SIZE - 2)
        if factor < 0.5:
            self.hide()
        else:
            self.show()


class LayerArea(VerticalScrollArea):

    changeScale = QtCore.pyqtSignal(float)

    def __init__(self, layerCount=200, parent=None):
        # TODO: do we need a default layer number? Should it be 200?
        super().__init__(parent)
        self.layerCount = layerCount
        self.layers = []
        self.layerHeight = BLOCK_SIZE
        self.initUI()

    def initUI(self):
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(5, 0, 0, 0)
        self.container = QtWidgets.QWidget()
        self.container.setLayout(self.layout)
        self.container.setContentsMargins(0, 0, 0, 0)

        # self.updateLayerCount(100)
        for i in range(self.layerCount):
            layer = LayerBar(i, self.layerHeight)
            self.layout.addWidget(layer.frame)
            self.layers.append(layer)
            self.changeScale.connect(layer.changeScale)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setMaximumWidth(342)  # TODO: calculate instead of hardcode
        self.setWidget(self.container)

    def wheelEvent(self, event):
        # Prevent scrolling with the mouse wheel
        if event.type() == QtCore.QEvent.Wheel:
            event.ignore()

    @QtCore.pyqtSlot(int)
    def updateLayerHeight(self, height):
        self.layerHeight = height

    @QtCore.pyqtSlot(int, int)
    def updateLayerCount(self, width, newSize):
        count = newSize // BLOCK_SIZE
        if self.layerCount < count:
            while self.layerCount < count:
                self.layerCount += 1
                layer = LayerBar(self.layerCount, self.layerHeight)
                print("ADDING")
                self.layout.addWidget(layer.frame)
                self.layers.append(layer)
                self.changeScale.connect(layer.changeScale)
        else:
            while self.layerCount > count:
                self.layerCount -= 1
                i = self.layout.count()
                print("REMOVING", i)
                self.layout.takeAt(i)


class Workspace(QtWidgets.QSplitter):
    """
    A splitter holding a layer area on the left and a note
    block area on the right.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layerWidget = LayerArea()
        self.noteBlockWidget = NoteBlockArea()
        self.timeBar = TimeBar()

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.timeBar)
        layout.addWidget(self.layerWidget)

        # fill vertical space taken by horizontal scrollbar
        spacer = QtWidgets.QWidget()
        spacer.setFixedHeight(SCROLL_BAR_SIZE)
        layout.addWidget(spacer)

        leftPanel = QtWidgets.QWidget()
        leftPanel.setLayout(layout)

        self.addWidget(leftPanel)
        self.addWidget(self.noteBlockWidget.view)
        self.setHandleWidth(2)

        self.noteBlockWidget.view.verticalScrollBar().valueChanged.connect(
            self.layerWidget.verticalScrollBar().setValue
        )
        self.noteBlockWidget.view.scaleChanged.connect(self.layerWidget.changeScale)
        self.noteBlockWidget.sceneSizeChanged.connect(self.layerWidget.updateLayerCount)
        self.noteBlockWidget.sceneSizeChanged.connect(
            self.layerWidget.updateLayerHeight
        )

    def setSingleScrollBar(self):
        """
        Add the workspace and a horizontal scrollbar to a
        vertical layout, creating a scrollbar at the bottom
        that spans both the layer box and the note block area.
        Remove the call to this function to have the scrollbar
        span just the note block area.
        """
        self.view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scrollBar = QtWidgets.QScrollBar()
        scrollBar.setOrientation(QtCore.Qt.Horizontal)
        scrollBar.setMinimum(0)
        scrollBar.setMaximum(150)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self)
        layout.addWidget(scrollBar)
        container = QtWidgets.QWidget()
        container.setLayout(layout)

    def resetWorkspace(self):
        self.layerWidget.initUI()
        self.noteBlockWidget.clear()

    def loadSong(self, notes, layers):
        pass
        # TODO: load notes to NoteBlockArea and layers to LayerArea here


class CentralArea(QtWidgets.QSplitter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.workspace = Workspace()
        self.piano = PianoScroll(keyCount=88, offset=9, validRange=(33, 57))
        self.initUI()

    def initUI(self):
        self.setOrientation(QtCore.Qt.Vertical)
        self.setHandleWidth(2)
        self.addWidget(self.workspace)
        self.addWidget(self.piano)
        # reserve just enough space for piano and let workspace occupy the rest
        pianoHeight = self.piano.piano.height()
        self.setSizes([1, pianoHeight])
        self.handle(1).setEnabled(False)  # make handle unmovable
        self.setStretchFactor(0, 1)  # set workspace to stretch
        self.setStretchFactor(1, 0)  # set piano to NOT stretch
        # TODO: perhaps a QVBoxLayout is more appropriate here?
        self.piano.piano.activeKeyChanged.connect(
            self.workspace.noteBlockWidget.setActiveKey
        )


class InstrumentButton(QtWidgets.QToolButton):
    """Buttons for the instrument selection in the toolbar"""

    def __init__(self, instrument, parent=None):
        super().__init__(parent)
        self.setCheckable(True)

        icon = QtGui.QIcon(
            appctxt.get_resource("images/instruments/{}.png".format(instrument))
        )
        # TODO: make icon for custom instruments
        self.setIcon(icon)
        self.setToolTip(
            "Change instrument to {}".format(" ".join(instrument.split("_")).title())
        )
