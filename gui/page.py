import customtkinter
from CTkMessagebox import CTkMessagebox


class Page:
    def __init__(self, parent: customtkinter.CTk):
        self.frame: customtkinter.CTkFrame = customtkinter.CTkFrame(parent, corner_radius=0, fg_color="transparent")
        self.frame.grid_columnconfigure(0, weight=1)
        self._frame_row = 0
        self._frame_col = 0
        self._padx = 20
        self._pady = 20

        self.title_font = customtkinter.CTkFont(size=20, weight="bold")
        self.large_font = customtkinter.CTkFont(size=18)
        self.small_font = customtkinter.CTkFont(size=12)

    def _get_next_frame_row(self) -> int:
        prev = self._frame_row
        self._frame_row += 1

        return prev

    def _insert_widget(self, widget: customtkinter.CTkBaseClass):
        widget.grid(row=self._get_next_frame_row(), column=self._frame_col, padx=self._padx, pady=self._pady)
