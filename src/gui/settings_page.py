import sys

import customtkinter
from src.gui.page import Page
import src.local_data.file_handler


class SettingsPage(Page):
    def __init__(self, parent, filehandler: src.local_data.file_handler.FileHandler):
        super().__init__(parent, "Settings")

        self.__filehandler = filehandler

        """ **************
        Secret Setter Frame 
        ************** """
        self.secret_setter_frame = customtkinter.CTkFrame(self.frame, corner_radius=0, fg_color="transparent")
        self._insert_widget(self.secret_setter_frame)

        self.client_textbox = customtkinter.CTkEntry(self.secret_setter_frame,
                                                     width=350,
                                                     placeholder_text="Client ID")
        self.client_textbox.grid(row=0, column=0, padx=10, pady=10)

        self.secret_textbox = customtkinter.CTkEntry(self.secret_setter_frame,
                                                     show="*",
                                                     width=350,
                                                     placeholder_text="Client Secret")
        self.secret_textbox.grid(row=1, column=0, padx=10, pady=10)

        self.save_credentials = customtkinter.CTkButton(self.secret_setter_frame,
                                                        text="Save",
                                                        command=self.__save_secrets_event)
        self.save_credentials.grid(row=2, column=0, padx=10, pady=10)

        """ **************
        Process Mode Frame 
        ************** """
        self.style_frame = customtkinter.CTkFrame(self.frame, corner_radius=0, fg_color="transparent")
        self._insert_widget(self.style_frame)

        self.default_style_label = customtkinter.CTkLabel(self.style_frame, text="Process Mode")
        self.default_style_label.grid(row=0, column=0, padx=10, pady=10)

        # Todo set event to save default
        self.process_mode = customtkinter.CTkOptionMenu(self.style_frame,
                                                        values=["Single-Photo", "Pair-Photo"],
                                                        command=self.__output_type_dd_change)
        self.process_mode.grid(row=0, column=1, padx=10, pady=10)
        self.output_type = self.process_mode.get()
        # Todo set it to the saved value

        # Process mode frames
        self.single_search_frame = customtkinter.CTkFrame(self.frame)
        self.pair_search_frame = customtkinter.CTkFrame(self.frame)

        # Single search settings
        self.search_profile_label = customtkinter.CTkLabel(self.single_search_frame, text="Search Profile")
        self.search_profile_label.grid(row=0, column=0, padx=10, pady=10)
        self.search_profile = customtkinter.CTkOptionMenu(self.single_search_frame,
                                                          values=filehandler.get_query_profile_names(),
                                                          command=self.__set_query_profile)
        self.search_profile.grid(row=0, column=1, padx=10, pady=10)

        # Pair search settings
        # TODO: not implemented
        self.search_profile_a_label = customtkinter.CTkLabel(self.pair_search_frame, text="Profile A")
        self.search_profile_a_label.grid(row=0, column=0, padx=10, pady=10)
        self.search_profile_a = customtkinter.CTkOptionMenu(self.pair_search_frame)
        self.search_profile_a.grid(row=0, column=1, padx=10, pady=10)
        self.search_profile_b_label = customtkinter.CTkLabel(self.pair_search_frame, text="Profile B")
        self.search_profile_b_label.grid(row=1, column=0, padx=10, pady=10)
        self.search_profile_b = customtkinter.CTkOptionMenu(self.pair_search_frame,
                                                            values=self.__filehandler.get_query_profile_names())
        self.search_profile_b.grid(row=1, column=1, padx=10, pady=10)

        self.__set_process_mode("Single-Photo")

    def __output_type_dd_change(self, value):
        self.output_type = value

    def __save_secrets_event(self):
        self.__filehandler.set_secrets(self.client_textbox.get(), self.secret_textbox.get())

    def __set_query_profile(self, value):
        self.__filehandler.set_query_profile(value)

    def __set_process_mode(self, mode: str):
        self.__output_type_dd_change(mode)

        # forget all others
        if mode == "Single-Photo":
            self.single_search_frame.grid(row=3, column=0, padx=10, pady=10)
        else:
            self.single_search_frame.grid_forget()

        if mode == "Pair-Photo":
            self.pair_search_frame.grid(row=3, column=0, padx=10, pady=10)
        else:
            self.pair_search_frame.grid_forget()
