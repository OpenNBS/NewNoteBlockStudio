from PyQt5 import QtWidgets
import qtawesome as qta


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
    "settings":         qta.icon('mdi.settings')
    # fmt: on
}


# File
newSongAction = QtWidgets.QAction(icons["new_song"], "New song")
openSongAction = QtWidgets.QAction(icons["open_song"], "Open song...")
saveSongAction = QtWidgets.QAction(icons["save_song"], "Save song")
saveSongAsAction = QtWidgets.QAction(icons["save_song"], "Save song as a new file...")
saveOptionsAction = QtWidgets.QAction("Save options...")
importPatternAction = QtWidgets.QAction("Import pattern...")
exportPatternAction = QtWidgets.QAction("Export pattern...")
importMidiAction = QtWidgets.QAction("Import MIDI...")
exportMidiAction = QtWidgets.QAction("Export MIDI...")
exportSchematicAction = QtWidgets.QAction("Export schematic...")
exportAudioAction = QtWidgets.QAction("Export as audio file...")
exportDatapackAction = QtWidgets.QAction("Export as data pack...")
exitAction = QtWidgets.QAction(icons["save_song_as"], "Exit")

# Playback
playPauseAction = QtWidgets.QPushButton(icons["play_pause"], "Play/Pause song")
stopAction = QtWidgets.QAction(icons["stop"], "Stop song")
fastForwardAction = QtWidgets.QAction(icons["save_song_as"], "Fast-forward song")
rewindAction = QtWidgets.QAction(icons["save_song_as"], "Rewind song")
loopAction = QtWidgets.QAction(icons["save_song_as"], "Toggle looping")
loopAction.setCheckable(True)
metronomeAction = QtWidgets.QAction(icons["save_song_as"], "Toggle metronome")
metronomeAction.setCheckable(True)

# Edit
undoAction = QtWidgets.QAction(icons["save_song_as"], "Undo")
redoAction = QtWidgets.QAction(icons["save_song_as"], "Redo")
copyAction = QtWidgets.QAction(icons["save_song_as"], "Copy")
cutAction = QtWidgets.QAction(icons["save_song_as"], "Cut")
pasteAction = QtWidgets.QAction(icons["save_song_as"], "Paste")
deleteAction = QtWidgets.QAction(icons["save_song_as"], "Delete")
selectAllAction = QtWidgets.QAction(icons["save_song_as"], "Select all")
clearSelectionAction = QtWidgets.QAction(icons["save_song_as"], "Clear selection")
invertSelectionAction = QtWidgets.QAction(icons["save_song_as"], "Invert selection")
selectAllLeftAction = QtWidgets.QAction(
    icons["save_song_as"], "Select all to the left <-"
)
selectAllRightAction = QtWidgets.QAction(
    icons["save_song_as"], "Select all to the right ->"
)
selectAllInstrumentAction = QtWidgets.QAction(icons["save_song_as"], "Select all {}")
selectAllButInstrumentAction = QtWidgets.QAction(
    icons["save_song_as"], "Select all but {}"
)
increaseKeyAction = QtWidgets.QAction(icons["save_song_as"], "Increase octave")
decreaseKeyAction = QtWidgets.QAction(icons["save_song_as"], "Decrease octave")
increaseAction = QtWidgets.QAction(icons["save_song_as"], "Increase key")
decreaseKeyAction = QtWidgets.QAction(icons["save_song_as"], "Decrease key")
expandSelectionAction = QtWidgets.QAction(icons["save_song_as"], "Expand selection")
compressSelectionAction = QtWidgets.QAction(icons["save_song_as"], "Compress selection")
transposeNotesAction = QtWidgets.QAction(
    icons["save_song_as"], "Transpose notes outside octave range"
)

# Edit modes
setEditMode = QtWidgets.QActionGroup()
setEditModeKeyAction = QtWidgets.QAction(
    icons["save_song_as"], "Edit note key", parent=setEditMode
)
setEditModeVelocityAction = QtWidgets.QAction(
    icons["save_song_as"], "Edit note velocity", parent=setEditMode
)
setEditModePanningAction = QtWidgets.QAction(
    icons["save_song_as"], "Edit note panning", parent=setEditMode
)
setEditModePitchAction = QtWidgets.QAction(
    icons["save_song_as"], "Edit note pitch", parent=setEditMode
)

# Settings
songInfoAction = QtWidgets.QAction(icons["save_song_as"], "Song info...")
songPropertiesAction = QtWidgets.QAction(icons["save_song_as"], "Song properties...")
songStatsAction = QtWidgets.QAction(icons["save_song_as"], "Song properties...")
deviceManagerAction = QtWidgets.QAction(icons["save_song_as"], "MIDI device manager...")
preferencesAction = QtWidgets.QAction(icons["save_song_as"], "Preferences...")

# About
websiteAction = QtWidgets.QAction(icons["save_song_as"], "Website...")
forumPageAction = QtWidgets.QAction(icons["save_song_as"], "Minecraft Forums page...")
wikiPageAction = QtWidgets.QAction(icons["save_song_as"], "Minecraft Wiki page...")
githubPageAction = QtWidgets.QAction(icons["save_song_as"], "GitHub...")
changelogAction = QtWidgets.QAction(icons["save_song_as"], "Changelog...")
donateAction = QtWidgets.QAction(icons["save_song_as"], "Donate...")
aboutAction = QtWidgets.QAction(icons["save_song_as"], "About...")
