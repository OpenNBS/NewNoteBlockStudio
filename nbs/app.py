import sys
import os
from PyQt5 import QtCore, QtWidgets
from nbs.mainwindow import MainWindow

def main():
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    # Create application
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("Minecraft Note Block Studio")

    # Enable support for high DPI displays and use high res icons
    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    # Create main window
    window = MainWindow()
    window.show()

    return app.exec_()
