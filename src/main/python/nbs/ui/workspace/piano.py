from typing import List, Sequence

from PyQt5 import QtCore, QtGui, QtWidgets

from .constants import *

__all__ = ["PianoWidget", "HorizontalAutoScrollArea"]


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
        self.animationPress.setDuration(100)
        self.animationPress.setEasingCurve(QtCore.QEasingCurve.InOutQuad)

        self.animationLift = QtCore.QPropertyAnimation(self, b"pos")
        self.animationLift.setDuration(100)
        self.animationLift.setEasingCurve(QtCore.QEasingCurve.InOutQuad)

        self.animationGroup = QtCore.QSequentialAnimationGroup(self)
        self.animationGroup.addAnimation(self.animationPress)
        self.animationGroup.addAnimation(self.animationLift)
        self.animationGroup.finished.connect(self.animationGroup.stop)

    def pressKey(self):
        if not self.isPressed:
            print("Pressed key", self.label)
            self.move(QtCore.QPoint(self.x(), self.y() + 5))
            self.keyPressed.emit(self.num)
            self.isPressed = True
            self.update()

    def releaseKey(self):
        if self.isPressed:
            print("Released key", self.label)
            self.move(QtCore.QPoint(self.x(), self.y() - 5))
            self.keyReleased.emit(self.num)
            self.isPressed = False
            self.update()

    @QtCore.pyqtSlot()
    def play(self):
        self.animationGroup.setCurrentTime(0)
        pressedPos = QtCore.QPoint(self.x(), self.y() + 5)
        self.animationPress.setStartValue(self.pos())
        self.animationPress.setEndValue(pressedPos)
        self.animationLift.setStartValue(pressedPos)
        self.animationLift.setEndValue(self.pos())
        self.animationGroup.start()

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
        print("Playing key", key)
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
