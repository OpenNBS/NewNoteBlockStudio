from typing import Sequence

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


class InstrumentPressComboBox(QtWidgets.QComboBox):
    def __init__(self, value: int = 0, disabled: bool = False, parent=None):
        super().__init__()
        self.setDisabled(disabled)
        self.addItem("Yes")
        self.addItem("No")


class InstrumentSettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Instrument Settings")
        self.instruments = default_instruments
        self.initUI()

    def setInstruments(self, instruments: Sequence[InstrumentInstance]):
        pass
        # self.instruments = instruments

    def initUI(self):
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
        self.table = QtWidgets.QTableWidget()
        self.table.setRowCount(len(self.instruments))
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Name", "Sound file", "Key", "Press"])

        self.table.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        # select one row at a time
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setDragDropOverwriteMode(False)

        tableHeader = self.table.horizontalHeader()
        tableHeader.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
        tableHeader.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)

        print(self.instruments)
        for row, instrument in enumerate(self.instruments):
            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(instrument.name))
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem())
            self.table.setCellWidget(row, 2, InstrumentKeySpinBox())  # instrument.key
            self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(instrument.press))
            self.table.setCellWidget(row, 3, QtWidgets.QCheckBox())

        self.layout.addWidget(self.table)

        # Footer buttons
        self.footer = QtWidgets.QHBoxLayout()
        self.layout.addLayout(self.footer)

        self.addInstrumentButton = QtWidgets.QPushButton("Add")
        # self.addInstrumentButton.clicked.connect(self.onAddInstrument)
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

        def addInstrument(self):
            pass
