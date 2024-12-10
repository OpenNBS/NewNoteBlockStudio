from typing import List

from PyQt5 import QtCore, QtWidgets

from nbs.core.data import Instrument


class StatusBar(QtWidgets.QStatusBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.instrumentLabel = QtWidgets.QLabel()
        self.instrumentLabel.setText("Instrument: Harp")
        self.addPermanentWidget(self.instrumentLabel, stretch=5)

        self.keyLabel = QtWidgets.QLabel()
        self.keyLabel.setText("Key: F#4")
        self.addPermanentWidget(self.keyLabel, stretch=4)

        self.tickLabel = QtWidgets.QLabel()
        self.tickLabel.setText("Tick: None")
        self.addPermanentWidget(self.tickLabel, stretch=4)

        self.layerLabel = QtWidgets.QLabel()
        self.layerLabel.setText("Layer: None")
        self.addPermanentWidget(self.layerLabel, stretch=4)

        self.selectedLabel = QtWidgets.QLabel()
        self.selectedLabel.setText("Selected: 0 / 500")
        self.addPermanentWidget(self.selectedLabel, stretch=5)

        self.soundsLabel = QtWidgets.QLabel()
        self.soundsLabel.setText("Sounds: 0 / 1024")
        self.addPermanentWidget(self.soundsLabel, stretch=5)

        self.midiDevicesLabel = QtWidgets.QLabel()
        self.midiDevicesLabel.setText("No connected MIDI devices")
        self.addWidget(self.midiDevicesLabel, stretch=10)

    @QtCore.pyqtSlot(object)
    def setInstrument(self, instrument: Instrument):
        self.instrumentLabel.setText(f"Instrument: {instrument.name}")

    @QtCore.pyqtSlot(int)
    def setKey(self, key: int):
        label = key
        self.keyLabel.setText(f"Key: {label}")

    @QtCore.pyqtSlot(int)
    def setTick(self, tick: int):
        self.tickLabel.setText(f"Tick: {tick}")

    @QtCore.pyqtSlot(int)
    def setLayer(self, layer: int):
        self.layerLabel.setText(f"Layer: {layer}")

    @QtCore.pyqtSlot(int)
    def setTotalBlocks(self, totalBlocks: int):
        self.totalBlocks = totalBlocks
        self.updateSelectedLabel()

    @QtCore.pyqtSlot(int)
    def setSelectedBlocks(self, selectedBlocks: int):
        self.selectedBlocks = selectedBlocks
        self.updateSelectedLabel()

    def updateSelectedLabel(self):
        self.selectedLabel.setText(
            f"Selected: {self.selectedBlocks} / {self.totalBlocks}"
        )

    @QtCore.pyqtSlot(int)
    def setSoundCount(self, sounds: int):
        if sounds >= 1024:
            self.soundsLabel.setStyleSheet("color: red")
        else:
            self.soundsLabel.setStyleSheet("color: black")
        self.soundsLabel.setText(f"Sounds: {sounds} / 1024")

    @QtCore.pyqtSlot(list)
    def setMidiDevices(self, devices: List[str]):
        if not devices:
            self.midiDevicesLabel.setText("No connected MIDI devices")
        else:
            self.midiDevicesLabel.setText(f"MIDI devices: f{', '.join(devices)}")
