from PyQt5 import QtWidgets
from fbs_runtime.application_context.PyQt5 import ApplicationContext

appctxt = ApplicationContext()

SCROLL_BAR_SIZE = QtWidgets.qApp.style().pixelMetric(
    QtWidgets.QStyle.PM_ScrollBarExtent
)

BLOCK_SIZE = 32

KEY_LABELS = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
