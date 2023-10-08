import sys

from PyQt6.QtWidgets import QApplication

from app import MainWindow


def application(uipath: str):
    app = QApplication(sys.argv)
    window = MainWindow(uipath)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    uipath = "./client.ui"
    application(uipath)