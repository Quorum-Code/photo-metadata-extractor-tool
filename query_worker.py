# TODO: verify program is fine with file commented
#
# from PyQt5.QtCore import QThread, pyqtSignal
# from ocr_lines import read_data
#
#
# class QueryWorker(QThread):
#     finished = pyqtSignal()
#     result_ready = pyqtSignal(str)  # Define the signal here
#     progress_updated = pyqtSignal(float)
#
#     def __init__(self, directory_path):
#         super().__init__()
#         self.directory_path = directory_path
#
#     def run(self):
#         result = read_data(self.directory_path, self.progress_updated)
#         self.result_ready.emit(result)  # Emit the signal when the result is ready
#         self.finished.emit()
#
#     #def run_query(self):
#      #   extract_query_data()
#       #  self.finished.emit()
