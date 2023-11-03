from PyQt5.QtCore import QThread, pyqtSignal
from ocr_lines_new import read_data

class QueryWorker(QThread):
    finished = pyqtSignal()
    result_ready = pyqtSignal(str)  # Define the signal here

    def __init__(self, directory_path):
        super().__init__()
        self.directory_path = directory_path

    def run(self):
        result = read_data(self.directory_path)
        self.result_ready.emit(result)  # Emit the signal when the result is ready
        self.finished.emit()