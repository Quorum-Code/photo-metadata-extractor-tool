import customtkinter
from gui.page import Page


class GettingStartedPage(Page):
    def __init__(self, parent: customtkinter.CTk):
        super().__init__(parent)

        # TITLE
        self.__title_text = customtkinter.CTkLabel(self.frame, text="Getting Started", font=self.title_font)
        self._insert_widget(self.__title_text)

        # EXTRACTION
        self.extraction_text = ("Select a folder containing photos to extract SuDocs from. The program will create a "
                                "CSV file which contains extracted text")

        self.__extraction_frame = customtkinter.CTkFrame(self.frame, corner_radius=0, fg_color="transparent")
        self.__extraction_text = customtkinter.CTkLabel(self.__extraction_frame,
                                                        text=self.extraction_text)
        self.__extraction_text.grid(row=0, column=0, padx=self._padx, pady=self._pady)
        self._insert_widget(self.__extraction_frame)

        # TODO: Links to documentation

        pass

    def get_next_frame_row(self):
        return
