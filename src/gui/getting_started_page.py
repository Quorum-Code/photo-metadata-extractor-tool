import customtkinter
from src.gui.page import Page


class GettingStartedPage(Page):
    def __init__(self, parent: customtkinter.CTk):
        super().__init__(parent, "Getting Started")

        # EXTRACTION
        self.extraction_text = ("Select a folder containing photos to extract SuDocs from. The program will create a "
                                "CSV file which contains extracted text")

        self.getting_started_text = ("Before extracting or querying a CSV make sure to set your OCLC credentials in the"
                                     " settings page. If you're processing SuDoc numbered documents then no changes "
                                     "need to be made to the default profile. \n\nFind more about the program here: \n"
                                     "https://github.com/Quorum-Code/photo-metadata-extractor-tool/wiki")

        self.__getting_started_frame = customtkinter.CTkFrame(self.frame, corner_radius=0, fg_color="transparent")
        self.__getting_started_text = customtkinter.CTkTextbox(self.__getting_started_frame, width=400)
        self.__getting_started_text.insert("0.0", self.getting_started_text)
        self.__getting_started_text.configure(state="disabled")
        self.__getting_started_text.grid(row=0, column=0, padx=self._padx, pady=self._pady)

        self._insert_widget(self.__getting_started_frame)

        # TODO: Links to documentation

        pass

    def get_next_frame_row(self):
        return
