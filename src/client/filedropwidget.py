from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, pyqtSignal


class FileDropWidget(QLabel):
    clicked = pyqtSignal()
    dropped = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText("Drop files here")
        self.setAcceptDrops(True)

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        self.clicked.emit()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        file_paths = [url.toLocalFile() for url in event.mimeData().urls()]
        self.dropped.emit(file_paths[0])
        print("\n".join(file_paths))