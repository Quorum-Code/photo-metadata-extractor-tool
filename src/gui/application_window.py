import customtkinter
from src.gui import extraction_page, settings_page, config_page, getting_started_page, extracted_data_processing_page
import src.local_data.file_handler as fh


class App(customtkinter.CTk):
    def __init__(self, filehandler: fh.FileHandler):
        super().__init__()
        self.filehandler = filehandler

        # Window settings
        self.title("Photo Metadata Extractor Tool")
        self.geometry("1200x800")

        # Side button setup
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Scale options
        self.scale_options = ["50%", "75%", "100%", "125%", "150%", "200%", "250%"]

        """ **************
        Nav Bar Frame 
        ************** """
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(5, weight=1)

        # NAVIGATION BUTTONS
        # - Getting Started
        self.__getting_started_button = customtkinter.CTkButton(self.navigation_frame,
                                                                corner_radius=0,
                                                                height=40,
                                                                border_spacing=10,
                                                                text="Getting Started",
                                                                fg_color="transparent",
                                                                text_color=("gray10", "gray90"),
                                                                anchor="w",
                                                                command=self.__getting_started_button_event)
        self.__getting_started_button.grid(row=0, column=0, sticky="ew")

        # - Extraction
        self.__extraction_button = customtkinter.CTkButton(self.navigation_frame,
                                                           corner_radius=0,
                                                           height=40,
                                                           border_spacing=10,
                                                           text="Extraction",
                                                           fg_color="transparent",
                                                           text_color=("gray10", "gray90"),
                                                           anchor="w",
                                                           command=self.__extraction_button_event)
        self.__extraction_button.grid(row=1, column=0, sticky="ew")

        # - Extraction Processing
        self.extraction_processing_button = customtkinter.CTkButton(self.navigation_frame,
                                                                    corner_radius=0,
                                                                    height=40,
                                                                    border_spacing=10,
                                                                    text="OCR Extraction Processsing",
                                                                    fg_color="transparent",
                                                                    text_color=("gray10", "gray90"),
                                                                    anchor="w",
                                                                    command=self.__extraction_processing_button_event)
        self.extraction_processing_button.grid(row=2, column=0, sticky="ew")

        # - Settings
        self.__settings_button = customtkinter.CTkButton(self.navigation_frame,
                                                         corner_radius=0,
                                                         height=40,
                                                         border_spacing=10,
                                                         text="Settings",
                                                         fg_color="transparent",
                                                         text_color=("gray10", "gray90"),
                                                         anchor="w",
                                                         command=self.settings_button_event)
        self.__settings_button.grid(row=3, column=0, sticky="ew")

        # - Configuration
        self.__configuration_button = customtkinter.CTkButton(self.navigation_frame,
                                                              corner_radius=0,
                                                              height=40,
                                                              border_spacing=10,
                                                              text="Configuration",
                                                              fg_color="transparent",
                                                              text_color=("gray10", "gray90"),
                                                              anchor="w",
                                                              command=self.configuration_button_event)
        self.__configuration_button.grid(row=4, column=0, sticky="ew")

        # Style menu
        self.style_menu = customtkinter.CTkOptionMenu(self.navigation_frame,
                                                      values=["Light", "Dark", "System"],
                                                      command=self.change_style_event)
        style = self.filehandler.get_style()
        self.style_menu.set(style)
        self.change_style_event(style)
        self.style_menu.grid(row=6, column=0, padx=20, pady=20, sticky="s")

        # Style menu
        self.scale_menu = customtkinter.CTkOptionMenu(self.navigation_frame,
                                                      values=self.scale_options,
                                                      command=self.change_scale_event)
        scale = self.filehandler.get_scale()
        self.scale_menu.set(scale)
        self.change_scale_event(scale)
        self.scale_menu.grid(row=7, column=0, padx=20, pady=20, sticky="s")

        # INITIALIZING PAGES
        # - Initialize Getting Started frame
        self.__getting_started = getting_started_page.GettingStartedPage(self)

        # - Initialize Settings frame
        self.settings = settings_page.SettingsPage(self, self.filehandler)

        # - Initialize Home frame
        self.__extraction_page = extraction_page.ExtractionPage(self,
                                                                self.filehandler,
                                                                self.settings)

        self.process_folder = "None"
        self.sudoc_file = "None"

        # - Initialize Extracted Data Processing frame
        self.__extraction_processing_page = extracted_data_processing_page.ProcessExtractedDataPage(self,
                                                                                                    self.settings)

        # - Initialize Configuration frame
        self.configuration = config_page.ConfigurationPage(self, self.filehandler)

        # - Initialize Info frame
        self.info_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")

        # Load home frame
        self.select_frame_by_name("getting_started")
        self.grab_set()

    def select_frame_by_name(self, name: str):
        # Update navigation button colors
        self.__getting_started_button.configure(
            fg_color=("gray75", "gray25") if name == "getting_started" else "transparent")
        self.__extraction_button.configure(
            fg_color=("gray75", "gray25") if name == "extraction" else "transparent")
        self.__settings_button.configure(
            fg_color=("gray75", "gray25") if name == "settings" else "transparent")
        self.__configuration_button.configure(
            fg_color=("gray75", "gray25") if name == "configuration" else "transparent")
        self.extraction_processing_button.configure(
            fg_color=("gray75", "gray25") if name == "extraction_processing" else "transparent")

        # Clear focus
        self.focus()

        # Set or forget frames
        if name == "getting_started":
            self.__getting_started.frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.__getting_started.frame.grid_forget()

        if name == "extraction":
            self.__extraction_page.frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.__extraction_page.frame.grid_forget()

        if name == "settings":
            self.settings.frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.settings.frame.grid_forget()

        if name == "configuration":
            self.configuration.frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.configuration.frame.grid_forget()

        if name == "extraction_processing":
            self.__extraction_processing_page.frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.__extraction_processing_page.frame.grid_forget()


    def __getting_started_button_event(self):
        self.select_frame_by_name("getting_started")

    def __extraction_button_event(self):
        self.select_frame_by_name("extraction")

    def settings_button_event(self):
        self.select_frame_by_name("settings")

    def configuration_button_event(self):
        self.select_frame_by_name("configuration")

    def info_button_event(self):
        self.select_frame_by_name("info")

    def change_style_event(self, style: str):
        customtkinter.set_appearance_mode(style)
        self.filehandler.save_style(style)

    def change_scale_event(self, size: str):
        self.filehandler.save_scale(size)
        size_float = int(size.replace("%", "")) / 100
        customtkinter.set_widget_scaling(size_float)

    def __extraction_processing_button_event(self):
        self.select_frame_by_name("extraction_processing")