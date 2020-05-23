from PyQt5 import QtCore, QtGui, QtWidgets
from fbs_runtime.application_context.PyQt5 import ApplicationContext
import qtawesome as qta
import math


appctxt = ApplicationContext()


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
        painter.drawText(textRect, QtCore.Qt.AlignCenter + QtCore.Qt.AlignBottom, self.label)
        painter.end()

    def eventFilter(self, obj, event):
        """
        Since widgets happens to grab the mouse whenever you click one,
        in order to allow sliding the mouse over the piano, we install
        an eventFilter on every piano key to detect when the mouse moves
        over a certain key, then tell that key to be pressed.
        """
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
            if self.currentKey is not None and moveEvent.buttons() == QtCore.Qt.LeftButton:
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
        labels = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
        self.layout = QtWidgets.QHBoxLayout()
        # Bigger margin on the top to accomodate raised black keys
        self.layout.setContentsMargins(10, 15, 10, 25)
        self.layout.setSpacing(2)

        for i in range(self.keyCount):
            rangeMin, rangeMax = self._validRange
            isOutOfRange = not (rangeMin <= i <= rangeMax)
            oct, key = divmod(i + self.offset, 12)
            label = labels[key] + str(oct)
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
        self.resize(2400, 160)

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
            xPos = self.keys[pos-1].x() + keyOffset
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
        rightEdge.setLeft(self.width()-50)
        mousePos = event.pos()
        self.mouseNearLeftEdge = leftEdge.contains(mousePos)
        self.mouseNearRightEdge = rightEdge.contains(mousePos)


class TimeRuler(QtWidgets.QWidget):

    markerChanged = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(32)
        self.offset = 0
        self.scale = 1
        self.tempo = 10.00
        self.markerPos = 0

    def timestr(self, seconds):
        seconds, ms = divmod(int(seconds * 1000), 1000)
        minutes, seconds = divmod(seconds, 60)
        return f"{minutes:02d}:{seconds:02d},{ms:03d}"

    def getTextRect(self, fm: QtGui.QFontMetrics, text, x=0, y=0):
        # Calling boundingRect just once returns a wrong size. See:
        # https://stackoverflow.com/a/32078341/9045426
        textRect = fm.boundingRect(text)
        textRect = fm.boundingRect(textRect, 0, text)
        textRect.moveCenter(QtCore.QPoint(x, y))
        #if textRect.left() < 0 and textRect.right() >= (textRect.width() / 2):
        #    textRect.moveLeft(1)
        #if textRect.right() > rect.width():
        #    textRect.moveRight(textRect.width() - 1)
        return textRect

    def paintEvent(self, event):
        rect = self.rect()
        mid = rect.height() / 2
        blocksize = 32 * self.scale
        painter = QtGui.QPainter()
        painter.begin(self)
        fm = painter.fontMetrics()
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtCore.Qt.white)
        painter.drawRect(rect)
        painter.setPen(QtCore.Qt.black)
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
                painter.drawText(textRect, QtCore.Qt.AlignHCenter + QtCore.Qt.AlignTop, text)
            x += blocksize
        # Top part
        # We start with the length occupied by 250ms on the song, then double it
        # (essentially halving the number of markings) until they're far enough apart
        timeInterval = 0.25
        distance = int(self.tempo / 4 * blocksize)
        minDistance = self.getTextRect(fm, self.timestr(0)).width() + 50
        while distance < minDistance:
            distance *= 2
            timeInterval *= 2
        startTime, startPos = divmod(self.offset, distance)
        startTime *= timeInterval
        for i, x in enumerate(range(-startPos, rect.width() + minDistance, distance)):
            painter.drawLine(x, mid - 2, x, mid)
            time = startTime + i * timeInterval
            text = self.timestr(time)
            y = mid / 2 - 1
            textRect = self.getTextRect(fm, text, x, y)
            painter.drawText(textRect, QtCore.Qt.AlignHCenter + QtCore.Qt.AlignTop, text)
        # Marker
        markerColor = QtCore.Qt.black
        pen = QtGui.QPen(markerColor)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(self.markerPos, 0, self.markerPos, self.height())
        painter.fillPath(self.getMarkerHead(self.markerPos), QtGui.QBrush(markerColor))
        painter.end()

    def getMarkerHead(self, pos):
        rect = QtCore.QRectF(pos - 8, 0, 16, 16)
        path = QtGui.QPainterPath()
        path.moveTo(rect.topLeft())
        path.lineTo(rect.topRight())
        path.lineTo(rect.left() + rect.width() / 2, rect.bottom())
        path.lineTo(rect.topLeft())
        return path

    def mouseReleaseEvent(self, event):
        pos = event.pos().x()
        self.markerPos = pos
        self.markerChanged.emit(pos)
        self.update()

    @QtCore.pyqtSlot(int)
    def setOffset(self, value):
        self.offset = value
        self.update()

    @QtCore.pyqtSlot(float)
    def setScale(self, value):
        self.scale = value
        self.update()


class NoteBlockView(QtWidgets.QGraphicsView):

    scaleChanged = QtCore.pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.currentScale = 1
        #self.setViewportMargins(0, 80, 0, 0)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)

    @QtCore.pyqtSlot()
    def setScale(self, value):
        self.resetTransform()
        self.currentScale = 1
        self.changeScale(value)

    @QtCore.pyqtSlot()
    def changeScale(self, factor):
        if 0.2 < self.currentScale * factor < 4:
            # TODO: Zoom in/out anyway, capping at the max/min scale level
            self.scale(factor, factor)
            self.currentScale *= factor
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
        self.scene().updateSceneSize()


class NoteBlockArea(QtWidgets.QGraphicsScene):
    """
    A scrolling area that holds the note blocks in a song.
    """

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
        start = int(rect.x() // 32)
        end = int(rect.right() // 32 + 1)
        for x in range(start, end):
            if x % 4 == 0:
                painter.setPen(QtGui.QColor(181, 181, 181))
            else:
                painter.setPen(QtGui.QColor(216, 216, 216))
            painter.drawLine(x*32, rect.y(), x*32, rect.bottom())

    def drawForeground(self, painter, rect):
        pen = QtGui.QPen(QtCore.Qt.black)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(self.markerPos, 0, self.markerPos, rect.height())

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
        self.markerPos = pos
        self.update()

    def updateSceneSize(self):
        if len(self.items()) > 1:
            bbox = self.itemsBoundingRect()
        else:
            bbox = QtCore.QRectF(0, 0, 0, 0)
        viewSize = self.view.rect()
        scrollBarSize = QtWidgets.qApp.style().pixelMetric(QtWidgets.QStyle.PM_ScrollBarExtent)
        # // 32 * 32, # - scrollBarSize - 32,
        newSize = (bbox.right() + viewSize.width(),
                   bbox.bottom() + viewSize.height())
        self.setSceneRect(QtCore.QRectF(0, 0, *newSize))

    def getGridPos(self, point):
        """
        Return the grid coordinates of a position in the scene.

        Args:
            point (QtCore.QPoint): the position to be converted

        Returns:
            tuple (int, int)
        """
        x = math.floor(point.x() / 32)
        y = math.floor(point.y() / 32)
        return x, y

    def getScenePos(self, x, y):
        """Return the top left scene position of a set of grid coordinates."""
        return QtCore.QPoint(x*32, y*32)

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
                if not QtGui.QGuiApplication.keyboardModifiers() == QtCore.Qt.ControlModifier:
                    self.clearSelection()
                self.selection.setStyleSheet("")
        self.selection.show()

    def mouseReleaseEvent(self, event):
        self.scrollSpeedX = 0
        self.scrollSpeedY = 0
        if self.isDraggingSelection:
            selectionArea = QtCore.QRectF(self.selection.geometry())
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
        if event.buttons() == QtCore.Qt.LeftButton or event.buttons() == QtCore.Qt.RightButton:
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
            x = math.floor(pos.x() / 32) * 32
            y = math.floor(pos.y() / 32) * 32
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
        elif event.buttons() == QtCore.Qt.LeftButton or event.buttons() == QtCore.Qt.RightButton:
            self.isDraggingSelection = True
            selectionRect = QtCore.QRectF(self.selectionStart, event.scenePos()).normalized().toRect()
            self.selection.setGeometry(selectionRect)
        else:
            # call the parent's mouseMoveEvent to allow
            # the scene items to detect hover events
            super().mouseMoveEvent(event)
            self.selection.hide()


class NoteBlock(QtWidgets.QGraphicsItem):

    labels = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")

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
        return QtCore.QRectF(0, 0, 32, 32)

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
        painter.drawText(labelRect, QtCore.Qt.AlignHCenter + QtCore.Qt.AlignBottom, self.label)
        painter.setPen(numberColor)
        painter.drawText(numberRect, QtCore.Qt.AlignHCenter + QtCore.Qt.AlignTop, self.clicks)
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

    def changeKey(self, value):
        self.key += value
        self.refresh()

    def refresh(self):
        self.label = self.getLabel()
        self.clicks = self.getClicks()
        self.update()

    def getLabel(self):
        octave, key = divmod(self.key + 9, 12)
        label = self.labels[key] + str(octave)
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

    def __init__(self, num, name="", volume=100, panning=100, locked=False, solo=False, parent=None):
        super().__init__(parent)
        self.num = num
        self.name = name
        self.volume = volume
        self.panning = panning
        self.locked = locked
        self.solo = solo
        self.icons = self.initIcons()
        self.initUI()

    def initIcons(self):
        return {
            "volume":           qta.icon("mdi.volume-high"),
            "stereo":           qta.icon("mdi.equalizer"),
            "lock_locked":      qta.icon("mdi.lock-outline"),
            "lock_unlocked":    qta.icon("mdi.lock-open-variant-outline"),
            "solo":             qta.icon("mdi.exclamation-thick"),
            "select_all":       qta.icon("mdi.select-all"),
            "insert":           qta.icon("mdi.plus-circle-outline"),  # mdi.plus-box
            "remove":           qta.icon("mdi.delete-outline"),  # mdi.trash-can
            "shift_up":         qta.icon("mdi.arrow-up-bold"),
            "shift_down":       qta.icon("mdi.arrow-down-bold")
        }

    def initUI(self):
        self.setIconSize(QtCore.QSize(20, 24))
        self.setFixedHeight(32)
        self.setMaximumWidth(342)  # TODO: calculate instead of hardcode
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
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
        self.nameBox.setPlaceholderText("Layer {}".format(self.num+1))
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


class LayerArea(VerticalScrollArea):
    def __init__(self, layerCount=200, parent=None):
        super().__init__(parent)
        self.layerCount = layerCount
        self.layers = []
        self.initUI()

    def initUI(self):
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(5, 0, 0, 0)
        self.container = QtWidgets.QWidget()
        self.container.setLayout(self.layout)
        self.container.setContentsMargins(0, 0, 0, 0)
        for i in range(self.layerCount):
            layer = LayerBar(i)
            self.layout.addWidget(layer.frame)
            self.layers.append(layer)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setMaximumWidth(342) # TODO: calculate instead of hardcode
        self.setWidget(self.container)


class Workspace(QtWidgets.QSplitter):
    """
    A splitter holding a layer area on the left and a note
    block area on the right, with a time ruler at the top.
    Responsible for the communication between all elements.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layerWidget = LayerArea()
        self.noteBlockWidget = NoteBlockArea()
        self.rulerWidget = TimeRuler(self)

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.rulerWidget)
        layout.addWidget(self.noteBlockWidget.view)

        container = QtWidgets.QWidget()
        container.setLayout(layout)

        self.addWidget(self.layerWidget)
        self.addWidget(container)
        self.setHandleWidth(2)

        self.noteBlockWidget.view.horizontalScrollBar().valueChanged.connect(self.rulerWidget.setOffset)
        self.noteBlockWidget.view.scaleChanged.connect(self.rulerWidget.setScale)
        self.rulerWidget.markerChanged.connect(self.noteBlockWidget.setMarkerPos)

    def setSingleScrollBar(self):
        """
        Add the workspace and a horizontal scrollbar to a
        vertical layout, creating a scrollbar at the bottom
        that spans both the layer box and the note block area.
        Remove the call to this function to have the scrollbar
        span just the note block area.
        """
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
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
        self.handle(1).setEnabled(False) # make handle unmovable
        self.setStretchFactor(0, 1) # set workspace to stretch
        self.setStretchFactor(1, 0) # set piano to NOT stretch
        # TODO: perhaps a QVBoxLayout is more appropriate here?
        self.piano.piano.activeKeyChanged.connect(self.workspace.noteBlockWidget.setActiveKey)


class InstrumentButton(QtWidgets.QToolButton):
    """Buttons for the instrument selection in the toolbar"""
    def __init__(self, instrument, parent=None):
        super().__init__(parent)
        self.setCheckable(True)

        icon = QtGui.QIcon(appctxt.get_resource("images/instruments/{}.png".format(instrument)))
        # TODO: make icon for custom instruments
        self.setIcon(icon)
        self.setToolTip("Change instrument to {}".format(" ".join(instrument.split("_")).title()))
