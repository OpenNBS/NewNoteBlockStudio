#from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QMenuBar, QMenu, QToolBar, QSizePolicy, QGraphicsScene, QGraphicsView
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import qtawesome as qta


class VerticalScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup()

    def setup(self):
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        #content = QWidget(self)
        #content.setSizePolicy(QSizePolicy.Preferred)
        #layout = QVBoxLayout(content)

        #self.setWidget(content)
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Resize:
            obj.setMinimumWidth(self.minimumSizeHint().width() + 40)
        return super().eventFilter(obj, event)


class PianoKey(QWidget):
    def __init__(self, label="", isBlack=False, isPressed=False, isOutOfRange=False, isActive=False, parent=None):
        super().__init__(parent)
        self.label = label
        self.isBlack = isBlack
        self.isPressed = isPressed
        self.isOutOfRange = isOutOfRange
        self.isActive = isActive

    def paintEvent(self, event):
        # Colors
        if self.isBlack:
            if self.isPressed:
                color = QColor(51, 102, 255)
            elif self.isOutOfRange:
                color = QColor(61, 15, 15)
            else:
                color = QColor(100, 100, 100) if self.isPressed else QColor(30, 30, 30)
            textColor = Qt.white
        else:
            if self.isPressed:
                color = QColor(51, 102, 255)
            elif self.isOutOfRange:
                color = QColor(234, 170, 168)
            else:
                color = QColor(230, 230, 230) if self.isPressed else QColor(255, 255, 255)
            textColor = Qt.black
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
        painter = QPainter()
        painter.begin(self)
        painter.fillRect(rect, color)
        painter.fillRect(bevel, bevelColor)
        pen = QPen(outlineColor)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRects(rect, bevel)
        painter.setPen(textColor)
        painter.drawText(textRect, Qt.AlignCenter + Qt.AlignBottom, self.label)
        painter.end()

    def mousePressEvent(self, event):
        self.isPressed = True
        self.repaint()

    def mouseReleaseEvent(self, event):
        self.isPressed = False
        self.repaint()


class PianoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init()

    def init(self):
        self.keys = []
        self.whiteKeys = []
        self.blackKeys = []
        self.blackPositions = [1, 4, 6, 9, 11]#[1, 3, 6, 8, 10]
        keys = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
        layout = QHBoxLayout()
        # Bigger margin on the top to accomodate raised black keys
        layout.setContentsMargins(10, 15, 10, 25)
        layout.setSpacing(2)

        for i in range(88):
            isOutOfRange = False
            if i < 33 or i > 57:
                isOutOfRange = True
            oct, key = divmod(i, 12)
            label = keys[key] + str(oct)
            isBlack = key in self.blackPositions
            if isBlack:
                key = PianoKey(label, True, False, isOutOfRange, parent=self)
                self.blackKeys.append(key)
            else:
                key = PianoKey(label, False, False, isOutOfRange, parent=self)
                self.whiteKeys.append(key)
                layout.addWidget(key)
            self.keys.append(key)

        self.setLayout(layout)
        self.resize(2400, 160)

    def arrangeBlackKeys(self):
        keyWidth = self.whiteKeys[0].width() / 1.6
        keyHeight = self.whiteKeys[0].height() / 1.6
        offset = self.whiteKeys[0].width() / 1.5
        yPos = self.whiteKeys[0].y() - 10

        for i in range(len(self.blackKeys)):
            oct, key = divmod(i, 5)
            pos = oct * 12 + self.blackPositions[key]
            xPos = self.keys[pos-1].x() + offset
            self.blackKeys[i].resize(keyWidth, keyHeight)
            self.blackKeys[i].move(xPos, yPos)
            self.blackKeys[i].raise_()

    def resizeEvent(self, event):
        self.arrangeBlackKeys()


def drawMenuBar(window):
    # Create menu bar
    menuBar = QMenuBar(parent=window)

    # File
    fileMenu = menuBar.addMenu("File")
    fileMenu.addAction("New song")
    fileMenu.addAction("Open song...")
    recentSongs = fileMenu.addMenu(QIcon(), 'Open recent')
    recentSongs.addSection(QIcon(), "No recent songs")
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

    toolbar = QToolBar(parent=window)
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

    spacer = QWidget()
    spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    toolbar.addWidget(spacer)
    toolbar.addAction("Compatible")

    return toolbar

def drawLayers(window):

    icons = {
        "volume":           qta.icon('mdi.volume-high'),
        "stereo":           qta.icon('mdi.equalizer'),
        "lock_locked":      qta.icon('mdi.lock-outline'),
        "lock_unlocked":    qta.icon('mdi.lock-open-variant-outline'),
        "solo":             qta.icon('mdi.exclamation-thick'),
        "select_all":       qta.icon('mdi.select-all'),
        "insert":           qta.icon('mdi.plus-circle-outline'), #mdi.plus-box
        "remove":           qta.icon('mdi.delete-outline'), #mdi.trash-can
        "shift_up":         qta.icon('mdi.arrow-up-bold'),
        "shift_down":       qta.icon('mdi.arrow-down-bold')
    }

    layout = QVBoxLayout()
    layout.setSpacing(0)
    layout.setContentsMargins(5, 5, 0, 0)

    for i in range(0, 25):
        innerLayout = QHBoxLayout()
        innerLayout.setContentsMargins(5, 0, 5, 0)

        nameBox = QLineEdit()
        nameBox.setFixedSize(76, 16)
        nameBox.setPlaceholderText("Layer {}".format(i+1))

        layer = QToolBar()
        layer.setIconSize(QSize(20, 24))
        layer.setFixedHeight(32)
        layer.setMaximumWidth(342) # calculate instead of hardcode
        layer.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        layer.addWidget(nameBox)
        layer.addAction(icons["volume"], "Volume")
        layer.addAction(icons["stereo"], "Stereo panning")
        layer.addAction(icons["lock_unlocked"], "Lock this layer")
        layer.addAction(icons["solo"], "Solo this layer")
        layer.addAction(icons["select_all"], "Select all note blocks in this layer")
        layer.addAction(icons["insert"], "Add empty layer here")
        layer.addAction(icons["remove"], "Remove this layer")
        layer.addAction(icons["shift_up"], "Shift layer up")
        layer.addAction(icons["shift_down"], "Shift layer down")
        layer.setLayout(innerLayout)

        innerLayout.addWidget(layer)

        frame = QFrame()
        frame.setFrameStyle(QFrame.Panel)
        frame.setFrameShadow(QFrame.Raised)
        frame.setLineWidth(1)
        frame.setLayout(innerLayout)
        #frame = QWidget()
        #frame.setLayout(innerLayout)

        layout.addWidget(frame)

    container = QWidget()
    container.setLayout(layout)
    container.setContentsMargins(0, 0, 0, 0)

    layerBox = VerticalScrollArea()
    layerBox.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    layerBox.setMaximumWidth(layer.width())
    layerBox.setWidget(container)

    return layerBox


def drawWorkspace(window):

    layerWidget = drawLayers(window)

    scene = QGraphicsScene()
    scene.setSceneRect(0, 0, 2000, 2000)
    view = QGraphicsView(scene, parent=window)

    #color = QColor()
    #color.setRgb(10, 10, 10)
    #brush = QBrush()
    #brush.setColor(color)
    #view.setBackgroundBrush(brush)

    pen = QPen()
    color = QColor()
    #pen.setWidth(10)

    x1, y1, x2, y2 = scene.sceneRect().getRect()
    for x in range(int(x2)):
        if x % 4 == 0:
            color.setRgb(127, 127, 127)
        else:
            color.setRgb(200, 200, 200)
        pen.setColor(color)
        line = QGraphicsLineItem()
        line.setLine(x*32, y1, x*32, y2)
        line.setPen(pen)
        scene.addItem(line)

    splitter = QSplitter()
    splitter.setHandleWidth(2)
    splitter.addWidget(layerWidget)
    splitter.addWidget(view)
    #splitter.setStretchFactor(0.5, 0.5)

    # We add the workspace and a horizontal scrollbar to a
    # vertical layout, so now we have a scrollbar at the bottom
    # that spans both the layer box and the note block area.
    # Comment this section to have the scrollbar span just
    # the note block area.
    #view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    #scrollBar = QScrollBar()
    #scrollBar.setOrientation(Qt.Horizontal)
    #scrollBar.setMinimum(0)
    #scrollBar.setMaximum(150)
    #layout = QVBoxLayout()
    #layout.setContentsMargins(0, 0, 0, 0)
    #layout.setSpacing(0)
    #layout.addWidget(splitter)
    #layout.addWidget(scrollBar)
    #container = QWidget()
    #container.setLayout(layout)

    return splitter


def drawPiano(window):
    piano = PianoWidget()

    pianoArea = QScrollArea(parent=window)
    pianoArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    pianoArea.setWidget(piano)

    return pianoArea


def drawMainArea(window):
    workspace = drawWorkspace(window)
    piano = drawPiano(window)

    #layout = QSplitter()
    #layout.setContentsMargins(0, 0, 0, 0)
    #layout.setSpacing(0)
    #layout.addWidget(workspace)
    #layout.addWidget(piano)

    #mainArea.setLayout(layout)
    #return mainArea

    splitter = QSplitter()
    splitter.setOrientation(Qt.Vertical)
    splitter.setHandleWidth(2)
    splitter.addWidget(workspace)
    splitter.addWidget(piano)

    return splitter
