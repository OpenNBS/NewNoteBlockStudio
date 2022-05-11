import os

from fbs_runtime.application_context.PyQt5 import ApplicationContext
from nbs.mainwindow import MainWindow
from PyQt5 import QtCore


class AppContext(ApplicationContext):
    def run(self):
        os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

        # Set application info
        self.app.setApplicationName("Minecraft Note Block Studio")

        # Enable support for high DPI displays and use high res icons
        self.app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
        self.app.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

        # Create main window
        window = MainWindow()
        window.show()

        return self.app.exec_()
