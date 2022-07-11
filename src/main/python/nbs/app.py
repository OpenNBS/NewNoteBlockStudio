import os
import sys

from fbs_runtime.application_context import cached_property
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from nbs.mainwindow import MainWindow
from PyQt5.QtCore import QElapsedTimer, QEvent, QObject, Qt
from PyQt5.QtWidgets import QApplication


class App(QApplication):

    profiler = QElapsedTimer()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setOrganizationName("Minecraft Note Block Studio")
        self.setApplicationName("Minecraft Note Block Studio")
        self.setApplicationVersion("0.0.1")
        # self.setWindowIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__), "icon.png")))


class AppContext(ApplicationContext):
    @cached_property
    def app(self):
        return App(sys.argv)

    def run(self):
        os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

        # Set application info
        self.app.setApplicationName("Minecraft Note Block Studio")

        # Enable support for high DPI displays and use high res icons
        self.app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        self.app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

        # Create main window
        window = MainWindow()
        window.show()

        return self.app.exec_()
