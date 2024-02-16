import customtkinter
import os
from PyQt5.QtCore import QThread, pyqtSignal
from PIL import Image
from customtkinter import filedialog
import ocr_lines


class HomePage:
    def __init__(self, parent):
        self.__parent = parent
        self.__file_character_limit = 40
        self.__photo_folder = "no folder selected"
        self.__sudoc_file = "no file selected"
        self.__file_icon_local_path = "icons\\folder-icon.png"

        # Reference to QThread must be stored or will be destroyed by garbage collector
        self.__thread_object: OCRHanlder = None

        # todo add error handling for no image found
        self.__file_icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), self.__file_icon_local_path)
        self.__file_icon = customtkinter.CTkImage(Image.open(self.__file_icon_path), size=(24, 24))

        self.home_frame = customtkinter.CTkFrame(self.__parent, corner_radius=0, fg_color="transparent")
        self.home_frame.grid_columnconfigure(0, weight=1)

        self.home_text = customtkinter.CTkLabel(self.home_frame, text="Home Page",
                                                font=customtkinter.CTkFont(size=20, weight="bold"))
        self.home_text.grid(row=0, column=0, padx=20, pady=20)

        # Sub Home frame - Photo folder frame
        self.photo_folder_frame = customtkinter.CTkFrame(self.home_frame, corner_radius=0)
        self.photo_folder_frame.grid(row=1, column=0, padx=10, pady=10)

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
                                                                  command=self.ask_photo_folder)
        self.select_photo_folder_button.grid(row=0, column=1, padx=10, pady=10)

        self.photo_folder_name = customtkinter.CTkLabel(self.photo_folder_frame, text=self.__photo_folder, anchor="w",
                                                        width=300)
        self.photo_folder_name.grid(row=0, column=2, padx=10, pady=10)

        # Process Subframe
        self.process_frame = customtkinter.CTkFrame(self.home_frame, corner_radius=0, fg_color="transparent")
        self.process_frame.grid(row=2, column=0, padx=10, pady=10)

        # Progress text
        self.progress_text = customtkinter.CTkLabel(self.process_frame, corner_radius=0,
                                                    text="No Photos being processed...")
        self.progress_text.grid(row=0, column=0)

        # Progress bar
        self.progress_bar = customtkinter.CTkProgressBar(self.process_frame, width=300)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=1, column=0, padx=10)

        self.process_photo_button = customtkinter.CTkButton(self.process_frame, text="Process Photos",
                                                            command=self.start_text_extraction)
        self.process_photo_button.grid(row=2, column=0, padx=10, pady=20)

        # Sub Home frame - SuDoc file frame
        self.sudoc_file_frame = customtkinter.CTkFrame(self.home_frame, corner_radius=0)
        self.sudoc_file_frame.grid(row=3, column=0, padx=10, pady=10)

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
                                                                command=self.ask_sudoc_file)
        self.select_sudoc_file_button.grid(row=0, column=1, padx=10, pady=10)

        self.sudoc_file_name = customtkinter.CTkLabel(self.sudoc_file_frame, text=self.__sudoc_file, anchor="w",
                                                      width=300)
        self.sudoc_file_name.grid(row=0, column=2, padx=10, pady=10)

        # Process Subframe
        self.query_frame = customtkinter.CTkFrame(self.home_frame, corner_radius=0, fg_color="transparent")
        self.query_frame.grid(row=4, column=0, padx=10, pady=10)

        # Progress text
        self.query_progress_text = customtkinter.CTkLabel(self.query_frame, corner_radius=0,
                                                          text="No Queries being processed...")
        self.query_progress_text.grid(row=0, column=0)

        # Progress bar
        self.query_progress_bar = customtkinter.CTkProgressBar(self.query_frame, width=300)
        self.query_progress_bar.set(0)
        self.query_progress_bar.grid(row=1, column=0, padx=10)

        self.process_photo_button = customtkinter.CTkButton(self.query_frame, text="Process Queries",
                                                            command=None)
        self.process_photo_button.grid(row=2, column=0, padx=10, pady=20)

    def ask_photo_folder(self):
        selected_folder = filedialog.askdirectory()

        if selected_folder != "":
            self.__photo_folder = selected_folder
            self.photo_folder_name.configure(text=self._trim_filename(self.__photo_folder))

    def ask_sudoc_file(self):
        selected_file = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])

        if selected_file != "":
            self.__sudoc_file = selected_file
            self.sudoc_file_name.configure(text=self._trim_filename(self.__sudoc_file))

    def _trim_filename(self, filename: str) -> str:
        if len(filename) > self.__file_character_limit:
            trim_index = len(filename) - self.__file_character_limit
            filename = f"...{filename[trim_index:]}"
        return filename

    def start_text_extraction(self):
        print("starting extractor")

        self.__thread_object = OCRHanlder()
        self.__thread_object.directory = self.__photo_folder
        self.__thread_object.is_finished.connect(self.__debug_is_finished)
        self.__thread_object.results_ready.connect(self.__debug_result_ready)
        self.__thread_object.progress_percent.connect(self.__debug_progress_percent)

        self.__thread_object.start()

        print("finished initializing extractor")
        return

    def __debug_is_finished(self):
        print("is_finished")

    def __debug_result_ready(self, text: str):
        print(f"result_ready: {text}")

    def __debug_progress_percent(self, percent: float):
        print(f"percent: {percent}")


class OCRHanlder(QThread):
    is_finished = pyqtSignal()
    results_ready = pyqtSignal(str)
    progress_percent = pyqtSignal(float)

    def __init__(self):
        super().__init__()
        self.directory = None

        return

    def run(self):
        print("started extraction")
        results = ocr_lines.read_data(self.directory, self.progress_percent)
        print(results)
        self.results_ready.emit(results)
        self.is_finished.emit()
        return results
