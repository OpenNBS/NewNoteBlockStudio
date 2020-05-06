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

        self.load_song("test.nbs")  # Testing

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

    def drawToolBar(self):
        icons = {
            "new_song":                     qta.icon('mdi.file-plus'),
            "open_song":                    qta.icon('mdi.folder-open'),
            "save_song":                    qta.icon('mdi.content-save'),
            "rewind":                       qta.icon('mdi.rewind'),
            "fast_forward":                 qta.icon('mdi.fast-forward'),
            "play":                         qta.icon('mdi.play'),
            "pause":                        qta.icon('mdi.pause'),
            "stop":                         qta.icon('mdi.stop'),
            "record":                       qta.icon('mdi.record'),
            "loop":                         qta.icon('mdi.repeat'),
            "loop_off":                     qta.icon('mdi.repeat-off'),
            "instrument_harp":              nbs.ui.components.InstrumentIcon('instrument_harp'),
            "instrument_double_bass":       nbs.ui.components.InstrumentIcon('instrument_double_bass'),
            "instrument_bass_drum":         nbs.ui.components.InstrumentIcon('instrument_bass_drum'),
            "instrument_snare":             nbs.ui.components.InstrumentIcon('instrument_snare'),
            "instrument_click":             nbs.ui.components.InstrumentIcon('instrument_click'),
            "instrument_guitar":            nbs.ui.components.InstrumentIcon('instrument_guitar'),
            "instrument_flute":             nbs.ui.components.InstrumentIcon('instrument_flute'),
            "instrument_bell":              nbs.ui.components.InstrumentIcon('instrument_bell'),
            "instrument_chime":             nbs.ui.components.InstrumentIcon('instrument_chime'),
            "instrument_xylophone":         nbs.ui.components.InstrumentIcon('instrument_xylophone'),
            "instrument_iron_xylophone":    nbs.ui.components.InstrumentIcon('instrument_iron_xylophone'),
            "instrument_cow_bell":          nbs.ui.components.InstrumentIcon('instrument_cow_bell'),
            "instrument_didgeridoo":        nbs.ui.components.InstrumentIcon('instrument_didgeridoo'),
            "instrument_bit":               nbs.ui.components.InstrumentIcon('instrument_bit'),
            "instrument_banjo":             nbs.ui.components.InstrumentIcon('instrument_banjo'),
            "instrument_pling":             nbs.ui.components.InstrumentIcon('instrument_pling'),
            "instrument_custom":            nbs.ui.components.InstrumentIcon('instrument_custom'),
            # TODO: make icon for custom instruments
            "undo":                         qta.icon('mdi.undo'),
            "redo":                         qta.icon('mdi.redo'),
            "cut":                          qta.icon('mdi.content-cut'),
            "copy":                         qta.icon('mdi.content-copy'),
            "paste":                        qta.icon('mdi.content-paste'),
            "delete":                       qta.icon('mdi.delete'),
            "select_all":                   qta.icon('mdi.select-all'),
            "song_instruments":             qta.icon('mdi.piano'),
            "song_info":                    qta.icon('mdi.information'),
            "song_properties":              qta.icon('mdi.label'),
            "song_stats":                   qta.icon('mdi.file-document-edit'),
            "midi_devices":                 qta.icon('mdi.usb'),
            "settings":                     qta.icon('mdi.settings')
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

        toolbar = QtWidgets.QToolBar(parent=self)
        toolbar.addAction(icons["new_song"], "New song", self.new_song)
        toolbar.addAction(icons["open_song"], "Open song", self.load_song)
        toolbar.addAction(icons["save_song"], "Save song")
        toolbar.addSeparator()
        toolbar.addAction(icons["rewind"], "Rewind")
        toolbar.addAction(icons["play"], "Play")
        toolbar.addAction(icons["stop"], "Stop")
        toolbar.addAction(icons["fast_forward"], "Fast-forward")
        toolbar.addAction(icons["record"], "Record key presses")
        toolbar.addAction(icons["loop"], "Toggle looping")
        toolbar.addSeparator()
        toolbar.addAction(icons["instrument_harp"], "Change instrument to Harp")
        toolbar.addAction(icons["instrument_double_bass"], "Change instrument to Double Bass")
        toolbar.addAction(icons["instrument_bass_drum"], "Change instrument to Bass Drum")
        toolbar.addAction(icons["instrument_snare"], "Change instrument to Snare Drum")
        toolbar.addAction(icons["instrument_click"], "Change instrument to Click")
        toolbar.addAction(icons["instrument_guitar"], "Change instrument to Guitar")
        toolbar.addAction(icons["instrument_flute"], "Change instrument to Flute")
        toolbar.addAction(icons["instrument_bell"], "Change instrument to Bell")
        toolbar.addAction(icons["instrument_chime"], "Change instrument to Chime")
        toolbar.addAction(icons["instrument_xylophone"], "Change instrument to Xylophone")
        toolbar.addAction(icons["instrument_iron_xylophone"], "Change instrument to Iron Xylophone")
        toolbar.addAction(icons["instrument_cow_bell"], "Change instrument to Cow Bell")
        toolbar.addAction(icons["instrument_didgeridoo"], "Change instrument to Didgeridoo")
        toolbar.addAction(icons["instrument_bit"], "Change instrument to Bit")
        toolbar.addAction(icons["instrument_banjo"], "Change instrument to Banjo")
        toolbar.addAction(icons["instrument_pling"], "Change instrument to Pling")
        for instrument in self.currentSong.custom_instruments:
            toolbbar.addAction(icons["instrument_custom"], "Change instrument to Custom")  # TODO: put in custom name
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
        """Loads a .nbs file into the current session. passing a filename overrides opening the file dialog"""
        # TODO: import header details, layers, etc.
        if not filename:
            dialog = QtWidgets.QFileDialog(self)
            dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
            dialog.setNameFilter("Note Block Songs *.nbs")
            # dialog.restoreState()
            if dialog.exec():
                filename = dialog.selectedFiles()[0]
                # dialog.saveState()
        self.currentSong = nbs.core.data.Song(filename=filename)
        self.centralWidget().workspace.resetWorkspace()
        # TODO: load layers
        for note in self.currentSong.notes:
            self.centralWidget().workspace.noteBlockWidget.addBlock(note.tick, note.layer, note.key, note.instrument)
