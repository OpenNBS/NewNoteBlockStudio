from typing import List, Optional, Sequence

from PyQt5 import QtCore, QtGui, QtWidgets

from .constants import *

__all__ = ["PianoWidget", "HorizontalAutoScrollArea"]


class PianoKeyGlowEffect(QtWidgets.QGraphicsEffect):
    # QGraphicsColorizeEffect uses a hardcoded 'Screen' blend mode, which
    # doesn't work well with white keys. This is a similar effect that
    # uses the 'Darken' blend mode instead.
    # See: https://stackoverflow.com/a/75142608/9045426

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        self.color = QtGui.QColor(255, 255, 255)
        self.strength = 0

    @QtCore.pyqtProperty(float)
    def strength(self) -> float:
        return self._strength

    @strength.setter
    def strength(self, value: float) -> None:
        self._strength = value
        self.update()

    @QtCore.pyqtProperty(QtGui.QColor)
    def color(self) -> QtGui.QColor:
        return self._color

    @color.setter
    def color(self, value: QtGui.QColor) -> None:
        self._color = value
        self.update()

    # TODO: We'd like to make the effect different for black and white keys,
    # but we can't access the key's properties from here. Maybe we can pass
    # the key as an argument to the effect's constructor?

    # The red tint on out-of-range keys, blue on active keys might have to
    # be moved here so we can override them completely when drawing the pressed
    # glow, without the need to redraw the key completely.

    def draw(self, painter: QtGui.QPainter) -> None:
        pixmap, offset = self.sourcePixmap()
        painter.drawPixmap(offset, pixmap)
        painter.setOpacity(self.strength)
        painter.setBrush(self.color)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setCompositionMode(QtGui.QPainter.CompositionMode_Darken)
        painter.drawRect(pixmap.rect())


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
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.installEventFilter(self)
        self.initAnimation()

    def initAnimation(self):
        self.animationPress = QtCore.QPropertyAnimation(self, b"pos")
        self.animationPress.setDuration(300)
        self.animationPress.setEasingCurve(QtCore.QEasingCurve.OutInQuad)

        effect = PianoKeyGlowEffect(self)
        effect.strength = 0.0
        effect.color = QtGui.QColor(255, 255, 0, 200)
        self.setGraphicsEffect(effect)

        # Create a Qt property animation for the color of the key
        self.animationColor = QtCore.QPropertyAnimation(effect, b"strength")
        self.animationColor.setDuration(300)
        self.animationColor.setEasingCurve(QtCore.QEasingCurve.OutQuad)
        self.animationColor.setStartValue(1.0)
        self.animationColor.setKeyValueAt(0.66, 1.0)
        self.animationColor.setEndValue(0)

    def pressKey(self):
        if self.isPressed:
            return
        print("Pressed key", self.label)
        self.animationPress.setCurrentTime(0)
        self.animationPress.stop()
        self.move(QtCore.QPoint(self.x(), self.y() + 5))
        self.keyPressed.emit(self.num)
        self.isPressed = True
        self.update()

    def releaseKey(self):
        if not self.isPressed:
            return
        print("Released key", self.label)
        self.animationPress.setCurrentTime(0)
        self.animationPress.stop()
        self.move(QtCore.QPoint(self.x(), self.y() - 5))
        self.keyReleased.emit(self.num)
        self.isPressed = False
        self.update()

    @QtCore.pyqtSlot()
    def play(self):
        self.animationColor.setCurrentTime(0)
        self.animationColor.start()

        # Don't play the press animation if the key is manually held down
        if self.isPressed:
            return

        self.animationPress.setCurrentTime(0)
        pressedPos = QtCore.QPoint(self.x(), self.y() + 5)
        self.animationPress.setStartValue(self.pos())
        self.animationPress.setEndValue(self.pos())
        self.animationPress.setKeyValueAt(0.5, pressedPos)
        self.animationPress.start()

    @property
    def isActive(self):
        return self._isActive

    @isActive.setter
    def isActive(self, value):
        self._isActive = value
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
            textColor = QtCore.Qt.GlobalColor.white
        else:
            if self.isActive:
                color = QtGui.QColor(51, 102, 255)
            elif self.isOutOfRange:
                color = QtGui.QColor(234, 170, 168)
            else:
                color = QtGui.QColor(255, 255, 255)
            if self.isPressed:
                color = color.darker(120)
            textColor = QtCore.Qt.GlobalColor.black
        bevelColor = color.darker(130)
        outlineColor = color.darker(200)

        # Geometry
        rect = self.rect()
        rect.setSize(QtCore.QSize(rect.width() - 1, rect.height() - 1))
        bevel = self.rect()
        bevel.setHeight(8)
        bevel.moveBottom(rect.bottom())
        textRect = self.rect()
        textRect.setBottom(bevel.top() - 15)

        # Paint
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.fillRect(rect, color)
        painter.fillRect(bevel, bevelColor)
        pen = QtGui.QPen(outlineColor)
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawRects(rect, bevel)
        painter.setPen(textColor)
        painter.drawText(
            textRect,
            QtCore.Qt.AlignmentFlag.AlignCenter | QtCore.Qt.AlignmentFlag.AlignBottom,
            self.label,
        )
        painter.end()

    def eventFilter(self, obj, event):
        # Since widgets happens to grab the mouse whenever you click one,
        # in order to allow sliding the mouse over the piano, we install
        # an eventFilter on every piano key to detect when the mouse moves
        # over a certain key, then tell that key to be pressed.
        if event.type() == QtCore.QEvent.Type.MouseButtonPress:
            self.pressKey()
        if event.type() == QtCore.QEvent.Type.MouseButtonRelease:
            self.releaseKey()
            if self.currentKey is not None:
                self.currentKey.releaseKey()
        if event.type() == QtCore.QEvent.Type.MouseMove:
            moveEvent = QtGui.QMouseEvent(event)
            widget = QtWidgets.qApp.widgetAt(moveEvent.globalPos())
            self.currentKey = widget if isinstance(widget, PianoKey) else None
            if self.previousKey is not None and self.previousKey != self.currentKey:
                self.previousKey.releaseKey()
            if (
                self.currentKey is not None
                and moveEvent.buttons() == QtCore.Qt.MouseButton.LeftButton
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

    @QtCore.pyqtSlot(int)
    def setActiveKey(self, key):
        self.activeKey = key

    def initUI(self):
        self.keys: List[PianoKey] = []
        self.whiteKeys: List[PianoKey] = []
        self.blackKeys: List[PianoKey] = []
        self.blackPositions = (1, 3, 6, 8, 10)
        self.layout = QtWidgets.QHBoxLayout()
        # Bigger margin on the top to accomodate raised black keys
        self.layout.setContentsMargins(10, 15, 10, 25)
        self.layout.setSpacing(1)

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
        self.resize(40 * len(self.whiteKeys), 160)  # TODO: hardcoded

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
        keyWidth = round(key.width() * 0.6)
        keyHeight = round(key.height() * 0.6)
        keyOffset = key.width() * 0.7
        yPos = key.y() - 6
        offset = self.blackKeysInRange(0, self.offset)
        for i in range(len(self.blackKeys)):
            oct, key = divmod(i + offset, 5)
            pos = oct * 12 + self.blackPositions[key] - self.offset
            # Set x pos based on the position of the previous (white) key
            xPos = round(self.keys[pos - 1].x() + keyOffset)
            self.blackKeys[i].resize(keyWidth, keyHeight)
            self.blackKeys[i].move(xPos, yPos)
            self.blackKeys[i].raise_()

    def resizeEvent(self, event):
        self.arrangeBlackKeys()

    @QtCore.pyqtSlot(int)
    def playKey(self, key: int) -> None:
        self.keys[key].play()

    @QtCore.pyqtSlot(list)
    def playKeys(self, keys: Sequence[int]) -> None:
        for key in keys:
            self.playKey(key)


class HorizontalAutoScrollArea(QtWidgets.QScrollArea):
    """
    A scrolling area with automatic scrolling when
    the mouse cursor is near the left or right edges.
    """

    def __init__(
        self,
        parent=None,
        updateDelay: int = 10,
        margins: int = 50,
        scrollAmount: int = 3,
    ):
        super().__init__(parent)
        self.margins = margins
        self.scrollAmount = scrollAmount
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.startTimer(updateDelay)

    def timerEvent(self, event: QtCore.QTimerEvent) -> None:
        self.checkAutoScroll()

    def checkAutoScroll(self) -> None:
        cursorPosition = self.mapFromGlobal(QtGui.QCursor.pos())
        sb = self.horizontalScrollBar()

        if self.rect().contains(cursorPosition):
            if cursorPosition.x() < self.margins:
                sb.setValue(sb.value() - self.scrollAmount)
            elif cursorPosition.x() > self.width() - self.margins:
                sb.setValue(sb.value() + self.scrollAmount)
