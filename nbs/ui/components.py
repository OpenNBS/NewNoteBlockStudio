from PyQt5 import QtCore, QtGui, QtWidgets
import qtawesome as qta
import math


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

    # Using the 'object' type since the value can
    # be either a number (int) or None (NoneType)
    keyPressed = QtCore.pyqtSignal(object)
    keyReleased = QtCore.pyqtSignal(object)

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
        '''
        Since widgets happens to grab the mouse whenever you click one,
        in order to allow sliding the mouse over the piano, we install
        an eventFilter on every piano key to detect when the mouse moves
        over a certain key, then tell that key to be pressed.
        '''
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
        self.repaint()

    @QtCore.pyqtSlot(object)
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


def drawMenuBar(window):
    menuBar = QtWidgets.QMenuBar(parent=window)

    # File
    fileMenu = menuBar.addMenu("File")
    fileMenu.addAction("New song")
    fileMenu.addAction("Open song...")
    recentSongs = fileMenu.addMenu(QtGui.QIcon(), 'Open recent')
    recentSongs.addSection(QtGui.QIcon(), "No recent songs")
    importMenu = fileMenu.addMenu("Import")
    importFromSchematicAction = importMenu.addAction("From schematic")
    importFromMidiAction = importMenu.addAction("From MIDI")
    fileMenu.addSeparator()
    saveSongAction = fileMenu.addAction("Save song")
    fileMenu.addAction("Save song as...")
    exportMenu = fileMenu.addMenu("Export as...")
    exportMenu.addAction("MIDI")
    exportMenu.addAction("Audio file")
    exportMenu.addAction("Schematic")
    exportMenu.addAction("Data pack")
    fileMenu.addSeparator()
    fileMenu.addAction("Exit")

    # Edit
    editMenu = menuBar.addMenu("Edit")

    # Settings
    settingsMenu = menuBar.addMenu("Settings")
    instrumentsMenu = settingsMenu.addMenu("Instrument")
    for ins in ["Harp", "Double Bass", "Bass Drum", "Snare Drum", "Click"]:
        instrumentsMenu.addAction(ins)
    settingsMenu.addSeparator()
    settingsMenu.addAction("Song info...")
    settingsMenu.addAction("Song properties...")
    settingsMenu.addAction("Song stats...")
    settingsMenu.addSeparator()
    settingsMenu.addAction("MIDI device manager...")
    settingsMenu.addAction("Save options...")
    settingsMenu.addAction("Preferences...")

    # Help
    helpMenu = menuBar.addMenu("Help")
    helpMenu.addAction("Changelog")

    return menuBar

def drawToolBar(window):
    icons = {
        "new_song":         qta.icon('mdi.file-plus'),
        "open_song":        qta.icon('mdi.folder-open'),
        "save_song":        qta.icon('mdi.content-save'),
        "rewind":           qta.icon('mdi.rewind'),
        "fast_forward":     qta.icon('mdi.fast-forward'),
        "play":             qta.icon('mdi.play'),
        "pause":            qta.icon('mdi.pause'),
        "stop":             qta.icon('mdi.stop'),
        "record":           qta.icon('mdi.record'),
        "loop":             qta.icon('mdi.repeat'),
        "loop_off":         qta.icon('mdi.repeat-off'),
        "undo":             qta.icon('mdi.undo'),
        "redo":             qta.icon('mdi.redo'),
        "cut":              qta.icon('mdi.content-cut'),
        "copy":             qta.icon('mdi.content-copy'),
        "paste":            qta.icon('mdi.content-paste'),
        "delete":           qta.icon('mdi.delete'),
        "select_all":       qta.icon('mdi.select-all'),
        "song_instruments": qta.icon('mdi.piano'),
        "song_info":        qta.icon('mdi.information'),
        "song_properties":  qta.icon('mdi.label'),
        "song_stats":       qta.icon('mdi.file-document-edit'),
        "midi_devices":     qta.icon('mdi.usb'),
        "settings":         qta.icon('mdi.settings')
    }
    '''
    icons = {
        "new_song": qta.icon('mdi.file'),
        "open_song": qta.icon('mdi.folder-open'),
        "save_song": qta.icon('mdi.save')
        "play": qta.icon('mdi.play')
        "pause": qta.icon('mdi.pause')
        "stop": qta.icon('mdi.stop')
        "loop_on":
        "loop_off":
        "undo":
        "redo":
    }
    '''

    toolbar = QtWidgets.QToolBar(parent=window)
    toolbar.addAction(icons["new_song"], "New song")
    toolbar.addAction(icons["open_song"], "Open song")
    toolbar.addAction(icons["save_song"], "Save song")
    toolbar.addSeparator()
    toolbar.addAction(icons["rewind"], "Rewind")
    toolbar.addAction(icons["play"], "Play")
    toolbar.addAction(icons["stop"], "Stop")
    toolbar.addAction(icons["fast_forward"], "Fast-forward")
    toolbar.addAction(icons["record"], "Record key presses")
    toolbar.addAction(icons["loop"], "Toggle looping")
    toolbar.addSeparator()
    toolbar.addAction(icons["undo"], "Undo")
    toolbar.addAction(icons["redo"], "Redo")
    toolbar.addAction(icons["cut"], "Cut")
    toolbar.addAction(icons["copy"], "Copy")
    toolbar.addAction(icons["paste"], "Paste")
    toolbar.addAction(icons["delete"], "Delete")
    toolbar.addSeparator()
    toolbar.addAction(icons["song_instruments"], "Instrument settings")
    toolbar.addAction(icons["song_info"], "Song info")
    toolbar.addAction(icons["song_properties"], "Song properties")
    toolbar.addAction(icons["song_stats"], "Song stats")
    toolbar.addAction(icons["midi_devices"], "MIDI device manager")
    toolbar.addAction(icons["settings"], "Settings")

    spacer = QtWidgets.QWidget()
    spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    toolbar.addWidget(spacer)
    toolbar.addAction("Compatible")

    return toolbar


class NoteBlockView(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)

    def wheelEvent(self, event):
        if event.modifiers() == QtCore.Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                zoomFactor = 1.25
            else:
                zoomFactor = 1 / 1.25
            self.scale(zoomFactor, zoomFactor)
        else:
            super().wheelEvent(event)


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
        self.initUI()

    def initUI(self):
        self.setSceneRect(0, 0, 32000, 32000)
        self.view.setCursor(QtCore.Qt.PointingHandCursor)
        self.view.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)
        self.selectionProxy = self.addWidget(self.selection)
        self.selectionProxy.setZValue(1)

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

    def addBlock(self, pos: QtCore.QPointF, *args, **kwargs):
        """Add a note block at the specified position."""
        x, y = self.getGridPos(pos)
        blockPos = self.getScenePos(x, y)
        block = NoteBlock(x, y, *args, **kwargs)
        block.setPos(blockPos)
        block.mouseOver = True
        self.addItem(block)

    def removeBlock(self, pos: QtCore.QPointF):
        """Remove the note block at the specified position."""
        x, y = self.getGridPos(pos)
        clicked = self.itemAt(pos, QtGui.QTransform())
        if isinstance(clicked, NoteBlock):
            self.removeItem(clicked)

    def setSelected(self, area, value=True):
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
        if self.isDraggingSelection:
            selectionArea = self.view.mapToScene(self.selection.geometry())
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
            if event.button() == QtCore.Qt.LeftButton:
                self.removeBlock(clickPos)
                self.addBlock(clickPos, 0, 5, 33, 0)
            elif event.button() == QtCore.Qt.RightButton:
                self.removeBlock(clickPos)

    def mouseMoveEvent(self, event):
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
        self.isOutOfRange = False
        self.mouseOver = False
        self.selected = False
        self.setAcceptHoverEvents(True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)

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
        blockColor = QtGui.QColor(60, 60, 255) # replace with instrument color
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
        pixmap = QtGui.QPixmap("images/note_block.png")
        painter.drawPixmap(rect, pixmap)
        brush = QtGui.QBrush(QtCore.Qt.SolidPattern)
        brush.setColor(blockColor)
        painter.setBrush(brush)
        painter.setCompositionMode(QtGui.QPainter.CompositionMode_Overlay)
        painter.drawRect(rect)
        painter.setCompositionMode(QtGui.QPainter.CompositionMode_SourceOver)
        painter.setOpacity(1)
        painter.setFont(font)
        painter.setPen(labelColor)
        painter.drawText(labelRect, QtCore.Qt.AlignHCenter + QtCore.Qt.AlignBottom, self.label)
        painter.setPen(numberColor)
        painter.drawText(numberRect, QtCore.Qt.AlignHCenter + QtCore.Qt.AlignTop, str(self.key))
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

    def getLabel(self):
        key, octave = divmod(self.key + 9, 12)
        label = self.labels[key] + str(octave)
        return label


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
            "insert":           qta.icon("mdi.plus-circle-outline"), #mdi.plus-box
            "remove":           qta.icon("mdi.delete-outline"), #mdi.trash-can
            "shift_up":         qta.icon("mdi.arrow-up-bold"),
            "shift_down":       qta.icon("mdi.arrow-down-bold")
        }

    def initUI(self):
        self.setIconSize(QtCore.QSize(20, 24))
        self.setFixedHeight(32)
        self.setMaximumWidth(342) # calculate instead of hardcode
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
        self.layout.setContentsMargins(5, 5, 0, 0)
        self.container = QtWidgets.QWidget()
        self.container.setLayout(self.layout)
        self.container.setContentsMargins(0, 0, 0, 0)
        for i in range(self.layerCount):
            layer = LayerBar(i)
            self.layout.addWidget(layer.frame)
            self.layers.append(layer)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setMaximumWidth(self.layers[0].width())
        self.setWidget(self.container)


class Workspace(QtWidgets.QSplitter):
    """
    A splitter holding a layer area on the left and a note
    block area on the right.
    """

    def __init__(self, layerWidget=None, noteBlockWidget=None, parent=None):
        super().__init__(parent)
        if layerWidget is None:
            self.layerWidget = LayerArea()
        else:
            self.layerWidget = layerWidget
        if noteBlockWidget is None:
            self.noteBlockWidget = NoteBlockArea()
        else:
            self.noteBlockWidget = noteBlockWidget
        self.addWidget(self.layerWidget)
        self.addWidget(self.noteBlockWidget.view)
        self.setHandleWidth(2)

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