from typing import Optional, Sequence

from nbs.controller.instrument import InstrumentInstance
from nbs.core.data import default_instruments
from PyQt5 import QtCore, QtGui, QtWidgets


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


class InstrumentSoundFileCell(QtWidgets.QTableWidgetItem):
    def __init__(self, value: str = "None", disabled: bool = False, parent=None):
        super().__init__(parent)
        self.setText(value)
        if disabled:
            self.setFlags(self.flags() & ~QtCore.Qt.ItemIsEnabled)
        self.disabled = disabled
        self.setLoaded(False)

    def setLoaded(self, loaded: Optional[bool] = True) -> None:
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
        checked: Optional[bool] = False,
        parent: QtWidgets.QWidget = None,
    ):
        super().__init__(parent)
        self.checkBox = QtWidgets.QCheckBox()
        self.checkBox.setChecked(checked)
        # QCheckBox.CheckState can be 0=unchecked, 1=partially checked, 2=checked
        self.checkBox.stateChanged.connect(lambda state: self.checked.emit(bool(state)))

        # Layout is needed so the checkbox is centered
        self.layout = QtWidgets.QHBoxLayout()
        self.layout.addWidget(self.checkBox)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.setLayout(self.layout)


class InstrumentTable(QtWidgets.QTableWidget):
    def __init__(self, instruments, parent=None):
        super().__init__(parent)
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["Name", "Sound file", "Key", "Press"])

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

        for row, instrument in enumerate(instruments):
            self.addRow(instrument)

    def addRow(self, instrument: InstrumentInstance, row: Optional[int] = None):
        row = row if row is not None else self.rowCount()

        nameColItem = QtWidgets.QTableWidgetItem(instrument.name)
        soundFileColItem = InstrumentSoundFileCell(
            instrument.soundPath, disabled=instrument.isDefault
        )
        keyColItem = InstrumentKeySpinBox(
            value=instrument.pitch, disabled=instrument.isDefault
        )
        pressColItem = InstrumentPressCheckBox(checked=instrument.press)

        self.insertRow(row)
        self.setItem(row, 0, nameColItem)
        self.setItem(row, 1, soundFileColItem)
        self.setCellWidget(row, 2, keyColItem)
        self.setCellWidget(row, 3, pressColItem)

        if instrument.isDefault:
            nameColItem.setFlags(nameColItem.flags() & ~QtCore.Qt.ItemIsEditable)
            soundFileColItem.setFlags(
                soundFileColItem.flags() & ~QtCore.Qt.ItemIsEditable
            )

        self.resizeRowToContents(row)


class InstrumentSettingsDialog(QtWidgets.QDialog):

    instrumentAddRequested = QtCore.pyqtSignal()

    def __init__(self, instruments, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Instrument Settings")
        self.instruments = instruments
        self.initUI()

    def setInstruments(self, instruments: Sequence[InstrumentInstance]):
        pass
        # self.instruments = instruments

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
        self.removeInstrumentButton = QtWidgets.QPushButton("Remove")
        # self.removeInstrumentButton.clicked.connect(self.onRemoveInstrument)
        self.footer.addWidget(self.removeInstrumentButton)
        self.shiftInstrumentUpButton = QtWidgets.QPushButton("Shift up")
        # self.shiftInstrumentUpButton.clicked.connect(self.onShiftInstrumentUp)
        self.footer.addWidget(self.shiftInstrumentUpButton)
        self.shiftInstrumentDownButton = QtWidgets.QPushButton("Shift down")
        # self.shiftInstrumentDownButton.clicked.connect(self.onShiftInstrumentDown)
        self.footer.addWidget(self.shiftInstrumentDownButton)

        self.okButton = QtWidgets.QPushButton("OK", clicked=self.accept)
        self.footer.addWidget(self.okButton)
        # self.cancelButton = QtWidgets.QPushButton("Cancel", self, clicked=self.reject)

        self.table.currentCellChanged.connect(self.updateSelection)

    @QtCore.pyqtSlot(int, int, int, int)
    def updateSelection(self, selectedRow, *_):
        if self.table.selectedItems():
            self.removeInstrumentButton.setEnabled(True)
            self.shiftInstrumentUpButton.setEnabled(selectedRow > 0)
            self.shiftInstrumentDownButton.setEnabled(
                selectedRow < self.table.rowCount() - 1
            )
        else:
            self.removeInstrumentButton.setEnabled(False)
            self.shiftInstrumentUpButton.setEnabled(False)
            self.shiftInstrumentDownButton.setEnabled(False)

    @QtCore.pyqtSlot()
    def onAddInstrument(self):
        # Request a new instrument be added
        self.instrumentAddRequested.emit()

    @QtCore.pyqtSlot(InstrumentInstance)
    def addInstrument(self, instrument: InstrumentInstance):
        self.table.addRow(instrument)
