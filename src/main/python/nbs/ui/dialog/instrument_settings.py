from typing import Optional, Sequence

from PyQt5 import QtCore, QtGui, QtWidgets

from nbs.controller.instrument import InstrumentInstance


def openSoundFileDialog() -> str:
    filename, _ = QtWidgets.QFileDialog.getOpenFileName(
        None,
        "Select sound file",
        "",
        "Sound files (*.wav *.mp3 *.ogg *.flac)",
    )
    return filename


class InstrumentKeySpinBox(QtWidgets.QSpinBox):
    def __init__(self, value: int = 45, disabled: bool = False, parent=None):
        super().__init__()
        self.setRange(0, 87)
        self.setValue(value)
        self.setDisabled(disabled)
        # self.setStyleSheet("border-style: none;")

    def textFromValue(self, value: int) -> str:
        keyNames = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        value += 9
        return keyNames[value % 12] + str(value // 12)

    def valueFromText(self, text: str) -> int:
        return super().valueFromText(text)


class InstrumentNameCell(QtWidgets.QTableWidgetItem):
    def __init__(self, value: str = "None", disabled: bool = False, parent=None):
        super().__init__(parent)
        self.setText(value)
        if disabled:
            self.setFlags(self.flags() & ~QtCore.Qt.ItemIsEnabled)
            self.setFlags(self.flags() & ~QtCore.Qt.ItemIsEditable)
            self.setForeground(QtCore.Qt.GlobalColor.gray)


class InstrumentSoundFileCell(QtWidgets.QTableWidgetItem):
    def __init__(self, value: str = "None", disabled: bool = False, parent=None):
        super().__init__(parent)
        self.setText(value)
        self.setLoaded(False)
        if disabled:
            self.setFlags(self.flags() & ~QtCore.Qt.ItemIsEnabled)
            self.setForeground(QtCore.Qt.GlobalColor.gray)
        self.setFlags(self.flags() & ~QtCore.Qt.ItemIsEditable)

    def setLoaded(self, loaded: bool = True) -> None:
        if loaded:
            self.setForeground(QtCore.Qt.GlobalColor.black)
            self.setToolTip("")
        else:
            self.setForeground(QtCore.Qt.GlobalColor.red)
            self.setToolTip("The sound file could not be loaded")


class InstrumentPressCheckBox(QtWidgets.QWidget):
    checked = QtCore.pyqtSignal(bool)

    def __init__(
        self,
        checked: bool = False,
        disabled: bool = False,
        parent: QtWidgets.QWidget = None,
    ):
        super().__init__(parent)
        self.checkBox = QtWidgets.QCheckBox()
        self.checkBox.setChecked(checked)
        self.checkBox.setDisabled(disabled)
        # QCheckBox.CheckState can be 0=unchecked, 1=partially checked, 2=checked
        self.checkBox.stateChanged.connect(lambda state: self.checked.emit(bool(state)))

        # Layout is needed so the checkbox is centered
        self.layout = QtWidgets.QHBoxLayout()
        self.layout.addWidget(self.checkBox)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.setLayout(self.layout)

    def setChecked(self, checked: bool) -> None:
        self.checkBox.setChecked(checked)


class InstrumentTable(QtWidgets.QTableWidget):

    soundNameCellChanged = QtCore.pyqtSignal(int, str)
    soundFileCellChanged = QtCore.pyqtSignal(int)
    soundKeyCellChanged = QtCore.pyqtSignal(int, int)
    soundPressCellChanged = QtCore.pyqtSignal(int, bool)

    def __init__(self, instruments: Sequence[InstrumentInstance], parent=None):
        super().__init__(parent)
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["Name", "Sound file", "Key", "Press"])
        self.lastAddedRow = 0

        # Select one row at a time
        self.setSelectionMode(QtWidgets.QTableWidget.SingleSelection)
        self.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)

        # Prevent resizing of columns, then set first two columns to stretch
        header = self.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)
        header.setHighlightSections(False)

        # Prevent resizing of rows
        vHeader = self.verticalHeader()
        vHeader.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Fixed)
        vHeader.setHighlightSections(False)

        for instrument in instruments:
            self.addRow(instrument)

        # Individual cells have no slots to report interactions such as
        # double-clicking and editing, so we must check for it on the entire table
        self.cellChanged.connect(self.onChangeCell)
        self.cellDoubleClicked.connect(self.onDoubleClickCell)

    def onChangeCell(self, row: int, col: int) -> None:
        # Since the setItem method triggers a cellChanged signal,
        # adding a new row causes this method to be called. To prevent
        # this, we check if the row was the last added row
        if col == 0 and row != self.lastAddedRow:
            self.soundNameCellChanged.emit(row, self.item(row, col).text())

    def onDoubleClickCell(self, row: int, col: int) -> None:
        if col == 1:
            self.soundFileCellChanged.emit(row)

    def addRow(self, instrument: InstrumentInstance, row: Optional[int] = None):
        row = row if row is not None else self.rowCount()
        self.lastAddedRow = row  # Used to prevent triggering onChangeCell on new row

        nameColItem = InstrumentNameCell(instrument.name, disabled=instrument.isDefault)
        soundFileColItem = InstrumentSoundFileCell(
            instrument.sound_path, disabled=instrument.isDefault
        )
        keyColItem = InstrumentKeySpinBox(
            value=instrument.pitch, disabled=instrument.isDefault
        )
        keyColItem.valueChanged.connect(
            lambda value: self.soundKeyCellChanged.emit(row, value)
        )
        pressColItem = InstrumentPressCheckBox(checked=instrument.press, disabled=False)
        pressColItem.checked.connect(
            lambda value: self.soundPressCellChanged.emit(row, value)
        )

        self.insertRow(row)
        self.setItem(row, 0, nameColItem)
        self.setItem(row, 1, soundFileColItem)
        self.setCellWidget(row, 2, keyColItem)
        self.setCellWidget(row, 3, pressColItem)
        self.resizeRowToContents(row)

    def editRow(self, row: int, instrument: InstrumentInstance):
        if row > self.rowCount() - 1:
            return
        self.item(row, 0).setText(instrument.name)
        self.item(row, 1).setText(instrument.sound_path)
        self.cellWidget(row, 2).setValue(instrument.pitch)
        self.cellWidget(row, 3).setChecked(instrument.press)

    def shiftRows(self, row1: int, row2: int) -> None:
        for col in range(self.columnCount()):
            item = self.takeItem(row1, col)
            self.setItem(row1, col, self.takeItem(row2, col))
            self.setItem(row2, col, item)
        self.setCurrentCell(row2, 0)


class InstrumentSettingsDialog(QtWidgets.QDialog):

    instrumentAddRequested = QtCore.pyqtSignal()
    instrumentRemoveRequested = QtCore.pyqtSignal(int)
    instrumentShiftRequested = QtCore.pyqtSignal(int, int)
    instrumentNameChangeRequested = QtCore.pyqtSignal(int, str)
    instrumentSoundFileChangeRequested = QtCore.pyqtSignal(int, str)
    instrumentKeyChangeRequested = QtCore.pyqtSignal(int, int)
    instrumentPressChangeRequested = QtCore.pyqtSignal(int, bool)

    def __init__(self, instruments, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Instrument Settings")
        self.instruments = instruments
        self.initUI()

    def initUI(self):
        self.resize(QtCore.QSize(640, 400))
        self.layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.layout)

        # Top paragraph
        self.info = QtWidgets.QLabel()
        self.info.setText(
            "These settings only apply to this song. To import the settings from another sound, click 'Import'. The sounds must be located in the 'Sounds' folder."
        )
        self.info.setWordWrap(True)

        # Top buttons
        self.topButtons = QtWidgets.QVBoxLayout()

        self.importButton = QtWidgets.QPushButton("Import from song")
        self.topButtons.addWidget(self.importButton)

        self.openFolderButton = QtWidgets.QPushButton("Open folder")
        self.topButtons.addWidget(self.openFolderButton)

        # Header
        self.header = QtWidgets.QHBoxLayout()
        self.header.addWidget(self.info)
        self.header.addLayout(self.topButtons)
        self.header.setStretchFactor(self.info, 1)
        self.layout.addLayout(self.header)

        # Instrument table
        self.table = InstrumentTable(self.instruments)
        self.layout.addWidget(self.table)

        # Footer buttons
        self.footer = QtWidgets.QHBoxLayout()
        self.layout.addLayout(self.footer)

        self.addInstrumentButton = QtWidgets.QPushButton(
            "Add", clicked=self.onAddInstrument
        )
        self.footer.addWidget(self.addInstrumentButton)
        self.removeInstrumentButton = QtWidgets.QPushButton(
            "Remove", clicked=self.onRemoveInstrument
        )
        self.footer.addWidget(self.removeInstrumentButton)
        self.shiftInstrumentUpButton = QtWidgets.QPushButton(
            "Shift up", clicked=self.onShiftInstrumentUp
        )
        self.footer.addWidget(self.shiftInstrumentUpButton)
        self.shiftInstrumentDownButton = QtWidgets.QPushButton(
            "Shift down", clicked=self.onShiftInstrumentDown
        )
        self.footer.addWidget(self.shiftInstrumentDownButton)

        self.okButton = QtWidgets.QPushButton("OK", clicked=self.accept)
        self.footer.addWidget(self.okButton)

        self.table.currentCellChanged.connect(self.updateSelection)
        self.table.soundNameCellChanged.connect(self.onInstrumentNameChanged)
        self.table.soundFileCellChanged.connect(self.onInstrumentSoundFileChanged)
        self.table.soundKeyCellChanged.connect(self.onInstrumentKeyChanged)
        self.table.soundPressCellChanged.connect(self.onInstrumentPressChanged)

    @QtCore.pyqtSlot(int, int, int, int)
    def updateSelection(self, selectedRow, *_):
        if self.table.selectedItems():
            self.removeInstrumentButton.setEnabled(True)
            self.shiftInstrumentUpButton.setEnabled(
                selectedRow > 16
            )  # TODO: replace with default instrument count
            self.shiftInstrumentDownButton.setEnabled(
                selectedRow < self.table.rowCount() - 1
            )
        else:
            self.removeInstrumentButton.setEnabled(False)
            self.shiftInstrumentUpButton.setEnabled(False)
            self.shiftInstrumentDownButton.setEnabled(False)

    # These signals request a change that will be handled externally,
    # which will emit the proper signals so the changes are reflected here.

    def onAddInstrument(self):
        # Request a new instrument be added
        self.instrumentAddRequested.emit()

    def onRemoveInstrument(self, id: int):
        self.instrumentRemoveRequested.emit(id)

    def onShiftInstrumentUp(self, id: int) -> None:
        if id < len(self.instruments):
            return
        self.instrumentShiftRequested.emit(id, -1)

    def onShiftInstrumentDown(self, id: int) -> None:
        if id > self.table.rowCount() - 1:
            return
        self.instrumentShiftRequested.emit(id, 1)

    def onInstrumentNameChanged(self, id: int, name: str) -> None:
        self.instrumentNameChangeRequested.emit(id, name)

    def onInstrumentSoundFileChanged(self, id):
        filename = openSoundFileDialog()
        if not filename:
            return
        self.instrumentSoundFileChangeRequested.emit(id, filename)

    def onInstrumentKeyChanged(self, id, key):
        self.instrumentKeyChangeRequested.emit(id, key)

    def onInstrumentPressChanged(self, id, press):
        self.instrumentPressChangeRequested.emit(id, press)

    # These signals do the actual work of visually updating the instrument table.

    @QtCore.pyqtSlot(InstrumentInstance)
    def addInstrument(self, instrument: InstrumentInstance):
        self.table.addRow(instrument)

    @QtCore.pyqtSlot(int)
    def removeInstrument(self, id: int):
        self.table.removeRow(id)

    @QtCore.pyqtSlot(int, InstrumentInstance)
    def editInstrument(self, id: int, instrument: InstrumentInstance) -> None:
        self.table.editRow(id, instrument)

    @QtCore.pyqtSlot(int, int)
    def shiftInstrument(self, id: int, shift: int):
        self.table.shiftRows(id, id + shift)
