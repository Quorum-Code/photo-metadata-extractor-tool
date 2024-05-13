import time
import typing

import customtkinter
from gui.page import Page
from CTkMessagebox import CTkMessagebox
import os
from PyQt5.QtCore import QThread, pyqtSignal
from PIL import Image
from customtkinter import filedialog
from ocr import ocr
from oclc.oclc_api import OCLCSession
import subprocess
from local_data.file_handler import FileHandler


class ExtractionPage(Page):
    def __init__(self, parent: customtkinter.CTk, file_handler: FileHandler):
        super().__init__(parent, "Extraction")

        self.__file_handler: FileHandler = file_handler
        self.__file_character_limit = 40
        self.__photo_folder = ""
        self.__sudoc_csv = ""
        self.__file_icon_local_path = "icons\\folder-icon.png"
        # Reference to QThread must be stored or will be destroyed by garbage collector
        self.__thread_object: OCRHandler | None = None
        # todo add error handling for no image found
        self.__file_icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), self.__file_icon_local_path)
        self.__file_icon = customtkinter.CTkImage(Image.open(self.__file_icon_path), size=(24, 24))

        # Sub Home frame - Photo folder frame
        self.photo_folder_frame = customtkinter.CTkFrame(self.frame, corner_radius=0)
        self._insert_widget(self.photo_folder_frame)

        self.photo_folder_name = customtkinter.CTkLabel(self.photo_folder_frame, text="Photo Folder", width=80)
        self.photo_folder_name.grid(row=0, column=0, padx=10, pady=10)

        self.select_photo_folder_button = customtkinter.CTkButton(self.photo_folder_frame,
                                                                  text="",
                                                                  image=self.__file_icon,
                                                                  height=10,
                                                                  width=10,
                                                                  border_spacing=0,
                                                                  corner_radius=0,
                                                                  fg_color="transparent",
                                                                  command=self.__ask_photo_folder)
        self.select_photo_folder_button.grid(row=0, column=1, padx=10, pady=10)

        self.photo_folder_name = customtkinter.CTkLabel(self.photo_folder_frame,
                                                        text=self.__format_file_text(self.__photo_folder),
                                                        anchor="w",
                                                        width=300)
        self.photo_folder_name.grid(row=0, column=2, padx=10, pady=10)

        # Process Subframe
        self.process_frame = customtkinter.CTkFrame(self.frame, corner_radius=0, fg_color="transparent")
        self._insert_widget(self.process_frame)

        # Progress text
        self.progress_text = customtkinter.CTkLabel(self.process_frame, corner_radius=0,
                                                    text="No Photos being processed...")
        self.progress_text.grid(row=0, column=0)

        # Progress bar
        self.progress_bar = customtkinter.CTkProgressBar(self.process_frame, width=300)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=1, column=0, padx=10)

        self.process_photo_button = customtkinter.CTkButton(self.process_frame, text="Process Photos",
                                                            command=self.__start_text_extraction)
        self.process_photo_button.grid(row=2, column=0, padx=10, pady=20)

        # Sub Home frame - SuDoc file frame
        self.sudoc_file_frame = customtkinter.CTkFrame(self.frame, corner_radius=0)
        self._insert_widget(self.sudoc_file_frame)

        self.sudoc_file_name = customtkinter.CTkLabel(self.sudoc_file_frame, text="SuDoc CSV", width=80)
        self.sudoc_file_name.grid(row=0, column=0, padx=10, pady=10)

        self.select_sudoc_file_button = customtkinter.CTkButton(self.sudoc_file_frame,
                                                                text="",
                                                                image=self.__file_icon,
                                                                height=10,
                                                                width=10,
                                                                border_spacing=0,
                                                                corner_radius=0,
                                                                fg_color="transparent",
                                                                command=self.__ask_sudoc_file)
        self.select_sudoc_file_button.grid(row=0, column=1, padx=10, pady=10)

        self.sudoc_file_name = customtkinter.CTkLabel(self.sudoc_file_frame,
                                                      text=self.__format_file_text(self.__sudoc_csv),
                                                      anchor="w",
                                                      width=300)
        self.sudoc_file_name.grid(row=0, column=2, padx=10, pady=10)

        # Process Subframe
        self.query_frame = customtkinter.CTkFrame(self.frame, corner_radius=0, fg_color="transparent")
        self._insert_widget(self.query_frame)

        # Progress text
        self.query_progress_text = customtkinter.CTkLabel(self.query_frame, corner_radius=0,
                                                          text="No Queries being processed...")
        self.query_progress_text.grid(row=0, column=0)

        # Progress bar
        self.query_progress_bar = customtkinter.CTkProgressBar(self.query_frame, width=300)
        self.query_progress_bar.set(0)
        self.query_progress_bar.grid(row=1, column=0, padx=10)

        self.process_photo_button = customtkinter.CTkButton(self.query_frame, text="Process Queries",
                                                            command=self.start_queries)
        self.process_photo_button.grid(row=2, column=0, padx=10, pady=20)

    def __ask_photo_folder(self):
        selected_folder = filedialog.askdirectory()

        if selected_folder != "":
            self.__photo_folder = selected_folder
            self.photo_folder_name.configure(text=self.__format_file_text(self.__photo_folder))

    def __ask_sudoc_file(self):
        selected_file = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])

        if selected_file != "":
            self.__sudoc_csv = selected_file
            self.sudoc_file_name.configure(text=self.__format_file_text(self.__sudoc_csv))

    def __format_file_text(self, filetext: str) -> str:
        if filetext == "":
            return "No file selected."
        elif len(filetext) > self.__file_character_limit:
            trim_index = len(filetext) - self.__file_character_limit
            return f"...{filetext[trim_index:]}"
        else:
            return filetext

    def __start_text_extraction(self):
        if not os.path.exists(self.__photo_folder):
            CTkMessagebox(title="ERROR", message="Please select a valid file.", icon="cancel")
            return

        self.__thread_object = OCRHandler(self.__set_query_file)
        self.__thread_object.progress_text = self.update_image_progress_text
        self.__thread_object.update_progress_bar = self.update_image_progress_percent
        self.__thread_object.directory = self.__photo_folder
        self.__thread_object.is_finished.connect(self.__debug_is_finished)
        self.__thread_object.results_ready.connect(self.__debug_result_ready)
        self.__thread_object.progress_percent.connect(self.__debug_progress_percent)
        self.__thread_object.start()

    def __set_query_file(self, file_path: str):
        self.__sudoc_csv = file_path
        formatted_path = self.__format_file_text(file_path)
        self.sudoc_file_name.configure(text=formatted_path)

    def update_query_progress_percent(self, percent: float):
        self.query_progress_bar.set(percent)

    def update_image_progress_text(self, text):
        self.progress_text.configure(text=text)

    def update_query_progress_text(self, text):
        self.query_progress_text.configure(text=text)

    def update_image_progress_percent(self, percent: float):
        self.progress_bar.set(percent)

    def start_queries(self):
        # Start OCLC session
        oclc = OCLCSession(self.__file_handler)
        if oclc.ready_session():
            print("Authorized")
        else:
            # Popup message and exit
            print("NOT Authorized")
            CTkMessagebox(title="ERROR", message="Invalid credentials or error getting tokens. Make sure your "
                                                 "credentials are properly set in the 'Settings' tab.", icon="cancel",
                          width=500, height=350)
            return

        self.__thread_object = QueryThread(oclc, self.__sudoc_csv,
                                           self.update_query_progress_percent,
                                           self.update_query_progress_text)
        self.__thread_object.start()
        return

    def __debug_is_finished(self):
        print("is_finished")

    def __debug_result_ready(self, text: str):
        print(f"result_ready: {text}")

    def __debug_progress_percent(self, percent: float):
        print(f"percent: {percent}")

    def __debug_progress_text(self, text: str):
        print(f"text: {text}")


class OCRHandler(QThread):
    is_finished = pyqtSignal()
    single_result_ready = pyqtSignal(str)
    results_ready = pyqtSignal(str)
    progress_percent = pyqtSignal(float)

    def __init__(self, update_file: typing.Callable[[str], None]):
        super().__init__()
        self.directory = None
        self.update_progress_bar = None
        self.progress_text = None

        self.update_file = update_file
        return

    def run(self):
        print("started extraction")
        self.progress_text("Text Extraction in Progress...")
        file_ct, result = ocr.main(self.directory, self.update_progress_bar)
        self.progress_text("Text Extraction Complete")
        print("before results_ready")
        self.results_ready.emit("Text Extraction Complete")
        print("after results_ready")
        self.is_finished.emit()
        self.update_file(result)
        return


class QueryThread(QThread):
    def __init__(self, oclc: OCLCSession, csv_path: str,
                 update_percent: typing.Callable, update_text: typing.Callable[[str], None]):
        super().__init__()
        self.__oclc = oclc
        self.__csv_path = csv_path
        self.__update_percent = update_percent
        self.__update_text = update_text

    def run(self):
        print("started")
        self.__update_text("Started querying...")
        self.__update_percent(0)

        self.__oclc.query_csv_sudoc(self.__csv_path, self.__update_percent)

        self.__update_percent(1)

        self.__update_text("Finished querying...")
        print("finished")
        return
