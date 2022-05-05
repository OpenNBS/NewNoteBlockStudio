from PyQt5 import QtCore, QtGui, QtWidgets
import qtawesome as qta
import nbs.ui.components
import nbs.core.data


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Minecraft Note Block Studio")
        self.setMinimumSize(854, 480)

        self.currentSong = nbs.core.data.Song()  # Initialize empty song object at the start of session

        menuBar = self.drawMenuBar()
        toolBar = self.drawToolBar()
        mainArea = nbs.ui.components.CentralArea(self)

        self.setMenuBar(menuBar)
        self.addToolBar(toolBar)
        self.setCentralWidget(mainArea)

    def drawMenuBar(self):
        menuBar = QtWidgets.QMenuBar(parent=self)

        # File
        fileMenu = menuBar.addMenu("File")
        fileMenu.addAction("New song", self.new_song)
        fileMenu.addAction("Open song...", self.load_song)
        recentSongs = fileMenu.addMenu(QtGui.QIcon(), 'Open recent')
        recentSongs.addSection(QtGui.QIcon(), "No recent songs")
        importMenu = fileMenu.addMenu("Import")
        importFromSchematicAction = importMenu.addAction("From schematic")
        importFromMidiAction = importMenu.addAction("From MIDI")
        fileMenu.addSeparator()
        saveSongAction = fileMenu.addAction("Save song", self.save_song)
        fileMenu.addAction("Save song as...", self.song_save_as)
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
        for ins in ["Harp", "Double Bass", "Bass Drum", "Snare Drum", "Click", "Guitar", "Flute", "Bell", "Chime",
                    "Xylophone", "Iron Xylophone", "Cow Bell", "Didgeridoo", "Bit", "Banjo", "Pling"]:
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

    def drawToolBar(self):
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

        instrument_list = ["harp", "double_bass", "bass_drum", "snare_drum", "click", "guitar", "flute", "bell",
                           "chime", "xylophone", "iron_xylophone", "cow_bell", "didgeridoo", "bit", "banjo", "pling"]
        instrument_button_list = [nbs.ui.components.InstrumentButton(instrument) for instrument in instrument_list]
        for instrument in self.currentSong.custom_instruments:  # TODO: reset custom instruments on new song
            instrument_button_list.append(nbs.ui.components.InstrumentButton("custom"))  # TODO: put in custom name

        instrument_buttons = QtWidgets.QButtonGroup(self)
        instrument_buttons.setExclusive(True)
        for button in instrument_button_list:
            instrument_buttons.addButton(button)

        toolbar = QtWidgets.QToolBar(parent=self)
        toolbar.addAction(icons["new_song"], "New song", self.new_song)
        toolbar.addAction(icons["open_song"], "Open song", self.load_song)
        toolbar.addAction(icons["save_song"], "Save song", self.save_song)
        toolbar.addSeparator()
        toolbar.addAction(icons["rewind"], "Rewind")
        toolbar.addAction(icons["play"], "Play")
        toolbar.addAction(icons["stop"], "Stop")
        toolbar.addAction(icons["fast_forward"], "Fast-forward")
        toolbar.addAction(icons["record"], "Record key presses")
        toolbar.addAction(icons["loop"], "Toggle looping")
        toolbar.addSeparator()
        for button in instrument_buttons.buttons():
            toolbar.addWidget(button)
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

    def drawStatusBar(self):
        pass

    @QtCore.pyqtSlot()
    def new_song(self):
        self.currentSong = nbs.core.data.Song()
        # TODO: save confirmation if editing unsaved work
        self.centralWidget().workspace.resetWorkspace()

    @QtCore.pyqtSlot()
    def load_song(self, filename=None):
        """Loads a .nbs file into the current session. passing a filename overrides opening the file dialog.
        loadFlag determines if the method is allowed to load the file and reset the workspace (needed in case the
        user presses cancel on the open file dialog)."""
        loadFlag = False

        if filename:
            loadFlag = True
        else:
            dialog = QtWidgets.QFileDialog(self)
            dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
            dialog.setWindowTitle("Open song")
            dialog.setLabelText(QtWidgets.QFileDialog.FileName, "Song name:")
            dialog.setNameFilter("Note Block Songs (*.nbs)")
            # dialog.restoreState()
            if dialog.exec():
                filename = dialog.selectedFiles()[0]
                # dialog.saveState()
                loadFlag = True

        if loadFlag:
            self.currentSong = nbs.core.data.Song(filename=filename)
            self.centralWidget().workspace.resetWorkspace()
            # TODO: load layers
            for note in self.currentSong.notes:
                self.centralWidget().workspace.noteBlockWidget.addBlock(note.tick, note.layer, note.key, note.instrument)
            # It's really weird to updateSceneSize() here, there has to be a better solution.
            self.centralWidget().workspace.noteBlockWidget.updateSceneSize()

        # TODO: The main window should only interact with the workspace (consisting of layer area + note block area),
        # not directly with the note block area. The workspace will do the talking between the layer and note block
        # areas, keeping them in sync, and also provide an interface for interacting with both at the same time.

    @QtCore.pyqtSlot()
    def save_song(self):
        """Save current file without bringing up the save dialog if it has a defined location on disk"""
        if not self.currentSong.location:
            self.song_save_as()
        else:
            self.currentSong.save()

    @QtCore.pyqtSlot()
    def song_save_as(self):
        dialog = QtWidgets.QFileDialog(self)
        dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
        dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        dialog.setWindowTitle("Save song")
        dialog.setLabelText(QtWidgets.QFileDialog.FileName, "Song name:")
        dialog.setNameFilter("Note Block Songs (*.nbs)")
        # dialog.restoreState()
        if dialog.exec():
            location = dialog.selectedFiles()[0]
            self.currentSong.save(location)
            # dialog.saveState()
