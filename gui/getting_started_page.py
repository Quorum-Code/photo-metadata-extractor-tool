import customtkinter
from gui.page import Page


class GettingStartedPage(Page):
    def __init__(self, parent: customtkinter.CTk):
        super().__init__(parent, "Getting Started")

        # EXTRACTION
        self.__extraction_frame = customtkinter.CTkFrame(self.frame, corner_radius=0, fg_color="transparent")
        self.__extraction_text = customtkinter.CTkLabel(self.__extraction_frame, text="Some text about extraction data")
        self.__extraction_text.grid(row=0, column=0, padx=self._padx, pady=self._pady)
        self._insert_widget(self.__extraction_frame)

        # TODO: Links to documentation

        pass

    def get_next_frame_row(self):
        return
