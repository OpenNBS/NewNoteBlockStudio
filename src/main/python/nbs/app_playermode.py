import os
import sys

from fbs_runtime.application_context import cached_property
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlApplicationEngine, qmlRegisterType

from nbs.ui.qml.playermode import NoteManager


class App(QGuiApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setOrganizationName("Minecraft Note Block Studio")
        self.setApplicationName("Minecraft Note Block Studio")
        self.setApplicationVersion("0.0.1")
        # self.setWindowIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__), "icon.png")))

        # Enable support for high DPI displays and use high res icons
        os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
        self.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        self.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)


class AppContext(ApplicationContext):
    @cached_property
    def app(self):
        return App(sys.argv)

    def run(self):
        engine = QQmlApplicationEngine()
        engine.quit.connect(self.app.quit)

        noteManager = NoteManager()

        context = engine.rootContext()
        context.setContextProperty("noteManager", noteManager)
        qmlRegisterType(NoteManager, "NoteBlockStudio", 1, 0, "NoteManager")

        engine.load("src/main/python/nbs/ui/qml/main.qml")

        return self.app.exec_()
