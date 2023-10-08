import asyncio
import traceback
import typing
import sys

from PyQt6.QtCore import QRunnable, QObject, pyqtSignal, pyqtSlot


class ThreadSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    update_text = pyqtSignal(str)


class Thread(QRunnable):
    def __init__(
        self,
        callable: typing.Callable | typing.Coroutine,
        *args,
        **kwargs
    ):
        super(Thread, self).__init__()

        self.callable = callable
        self.args = args
        self.kwargs = kwargs

        self.signals = ThreadSignals()
        self.kwargs['callback'] = self.signals.update_text

    @pyqtSlot()
    def run(self):
        try:
            result = self.callable(*self.args, **self.kwargs)
            if isinstance(result, typing.Coroutine):
                result = asyncio.run(result)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()