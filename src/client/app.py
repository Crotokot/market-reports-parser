from pathlib import Path

from PyQt6 import uic, QtWidgets
from PyQt6.QtCore import QThreadPool, QMutex, QTimer

from threads import Thread
import handlers
from filedropwidget import FileDropWidget
from handlers import parsers


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, uipath: str):
        super(MainWindow, self).__init__()
        uic.load_ui.loadUi(uipath, self)

        self.threadpool = QThreadPool(self)
        self.mutex = QMutex()
        self.filename: str = None
        self.initialize_elements()

    def initialize_elements(self):
        self.upload_area: FileDropWidget = self.findChild(QtWidgets.QLabel, "upload_area")
        self.send_button = self.findChild(QtWidgets.QPushButton, "send_button")
        self.input_text_area = self.findChild(QtWidgets.QTextEdit, "input_text_area")
        self.output_text_area = self.findChild(QtWidgets.QTextBrowser, "output_text_area")

        self.connect_actions()

    def connect_actions(self):
        self.send_button.clicked.connect(self.send_data)
        self.upload_area.clicked.connect(self.upload_file)
        self.upload_area.dropped.connect(self.upload_file)

    def send_data(self):
        text = self.input_text_area.toPlainText()
        if text:
            self.send_button.setEnabled(False)
            self.upload_area.setEnabled(False)
            self.output_text_area.clear()
            action = Thread(handlers.send_data, content=text)
            action.signals.update_text.connect(self.notify)
            action.signals.finished.connect(self.finish_task)
            self.threadpool.start(action)

    def notify(self, result: str):
        def update_text():
            if self.result:
                self.current_text += self.result[0]
                self.result = self.result[1:]
                self.output_text_area.setText(self.current_text)
        self.mutex.lock()
        self.current_text = self.output_text_area.toPlainText()
        self.result = result
        self.timer = QTimer()
        self.timer.timeout.connect(update_text)
        self.timer.start(50)  # Updates every 100 milliseconds
        self.mutex.unlock()

    def upload_file(self, filename: str = None):
        if filename is None:
            filename, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, filter="Files (*.html *.pdf, *.txt)"
            )

        path = Path(filename)
        parser = parsers.parser_factory(path.suffix[1:])
        text = parser.parse(path.read_bytes())
        self.input_text_area.setText(text)

    def finish_task(self):
        self.send_button.setEnabled(True)
        self.upload_area.setEnabled(True)