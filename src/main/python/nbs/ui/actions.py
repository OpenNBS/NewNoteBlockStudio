from PyQt5.QtWidgets import QAction, QActionGroup, QPushButton
from PyQt5.QtGui import QIcon
import qtawesome as qta


class Actions:
    @classmethod
    def initActions(cls):

        # qta.icon can't be on the top level of the module, so we must
        # put everything into a method and call it after QApplication
        # is created. See https://github.com/spyder-ide/qtawesome/issues/144

        # TODO: There's probably a better way to do this...

        icons = {
            # fmt: off
            "new_song":         qta.icon('mdi.file-plus'),
            "open_song":        qta.icon('mdi.folder-open'),
            "save_song":        qta.icon('mdi.content-save'),
            "rewind":           qta.icon('mdi.rewind'),
            "fast_forward":     qta.icon('mdi.fast-forward'),
            "play_pause":       qta.icon('mdi.play', active='mdi.pause'),
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
            "settings":         qta.icon('mdi.cog'),
            "":                 QIcon()
            # fmt: on
        }

        # File
        cls.newSongAction = QAction(icons["new_song"], "New song")
        cls.openSongAction = QAction(icons["open_song"], "Open song...")
        cls.saveSongAction = QAction(icons["save_song"], "Save song")
        cls.saveSongAsAction = QAction(icons["save_song"], "Save song as a new file...")
        cls.saveOptionsAction = QAction("Save options...")
        cls.importPatternAction = QAction("Import pattern...")
        cls.exportPatternAction = QAction("Export pattern...")
        cls.importMidiAction = QAction("Import MIDI...")
        cls.exportMidiAction = QAction("Export MIDI...")
        cls.exportSchematicAction = QAction("Export schematic...")
        cls.exportAudioAction = QAction("Export as audio file...")
        cls.exportDatapackAction = QAction("Export as data pack...")
        cls.exitAction = QAction("Exit")

        # Playback
        cls.playPauseAction = QPushButton(icons["play_pause"], "Play/Pause song")
        cls.stopAction = QAction(icons["stop"], "Stop song")
        cls.fastForwardAction = QAction(icons["fast_forward"], "Fast-forward song")
        cls.rewindAction = QAction(icons["rewind"], "Rewind song")
        cls.loopAction = QAction(icons["loop"], "Toggle looping")
        cls.loopAction.setCheckable(True)
        cls.metronomeAction = QAction(icons[""], "Toggle metronome")
        cls.metronomeAction.setCheckable(True)

        # Edit
        cls.undoAction = QAction(icons["undo"], "Undo")
        cls.redoAction = QAction(icons["redo"], "Redo")
        cls.copyAction = QAction(icons["copy"], "Copy")
        cls.cutAction = QAction(icons["cut"], "Cut")
        cls.pasteAction = QAction(icons["paste"], "Paste")
        cls.deleteAction = QAction(icons["delete"], "Delete")
        cls.selectAllAction = QAction(icons["select_all"], "Select all")
        cls.deselectAllAction = QAction(icons[""], "Deselect all")
        cls.invertSelectionAction = QAction(icons[""], "Invert selection")
        cls.selectAllLeftAction = QAction(icons[""], "Select all to the left <-")
        cls.selectAllRightAction = QAction(icons[""], "Select all to the right ->")
        cls.selectAllInstrumentAction = QAction(icons[""], "Select all {}")
        cls.selectAllButInstrumentAction = QAction(icons[""], "Select all but {}")
        cls.increaseOctaveAction = QAction(icons[""], "Increase octave")
        cls.decreaseOctaveAction = QAction(icons[""], "Decrease octave")
        cls.increaseKeyAction = QAction(icons[""], "Increase key")
        cls.decreaseKeyAction = QAction(icons[""], "Decrease key")
        cls.expandSelectionAction = QAction(icons[""], "Expand selection")
        cls.compressSelectionAction = QAction(icons[""], "Compress selection")
        cls.transposeNotesAction = QAction(
            icons[""], "Transpose notes outside octave range"
        )

        # Edit modes
        cls.setEditMode = QActionGroup(None)
        cls.setEditModeKeyAction = QAction(
            icons[""], "Edit note key", parent=cls.setEditMode
        )
        cls.setEditModeVelocityAction = QAction(
            icons[""], "Edit note velocity", parent=cls.setEditMode
        )
        cls.setEditModePanningAction = QAction(
            icons[""], "Edit note panning", parent=cls.setEditMode
        )
        cls.setEditModePitchAction = QAction(
            icons[""], "Edit note pitch", parent=cls.setEditMode
        )

        # Settings
        cls.instrumentSettingsAction = QAction(icons[""], "Instrument settings...")
        cls.songInfoAction = QAction(icons[""], "Song info...")
        cls.songPropertiesAction = QAction(icons[""], "Song properties...")
        cls.songStatsAction = QAction(icons[""], "Song stats...")
        cls.deviceManagerAction = QAction(icons[""], "MIDI device manager...")
        cls.preferencesAction = QAction(icons[""], "Preferences...")

        # About
        cls.websiteAction = QAction(icons[""], "Website...")
        cls.githubAction = QAction(icons[""], "GitHub...")
        cls.discordAction = QAction(icons[""], "Discord server...")
        cls.reportBugAction = QAction(icons[""], "Report a bug...")
        cls.donateAction = QAction(icons[""], "Donate...")
        cls.changelogAction = QAction(icons[""], "Changelog...")
        cls.aboutAction = QAction(icons[""], "About...")
