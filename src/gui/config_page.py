import tkinter
import json
import customtkinter
from CTkMessagebox import CTkMessagebox

import src.local_data.file_handler as fh
from src.gui.page import Page


class ConfigurationPage(Page):
    def __init__(self, parent, file_handler: fh.FileHandler):
        super().__init__(parent, "Configuration")

        self.__file_handler = file_handler
        self.popup_window = None

        # Token Request config
        self.token_request_frame = customtkinter.CTkFrame(self.frame, corner_radius=5)
        self._insert_widget(self.token_request_frame)

        self.token_header_label = customtkinter.CTkLabel(self.token_request_frame, text="Token Config")
        self.token_header_label.grid(row=0, column=0)

        self.token_header_textbox = customtkinter.CTkTextbox(self.token_request_frame, height=150, width=500)
        self.token_header_textbox.grid(row=1, column=0, padx=10, pady=10)

        # Query Request config
        self.query_request_frame = customtkinter.CTkFrame(self.frame, corner_radius=5)
        self._insert_widget(self.query_request_frame)

        self.query_header_label = customtkinter.CTkLabel(self.query_request_frame, text="Query Config")
        self.query_header_label.grid(row=0, column=0)

        self.query_header_textbox = customtkinter.CTkTextbox(self.query_request_frame, height=150, width=500)
        self.query_header_textbox.grid(row=1, column=0, padx=10, pady=10)

        # self.query_parameters_label = customtkinter.CTkLabel(self.query_request_frame, text="Query Request Paramenters")
        # self.query_parameters_label.grid(row=0, column=1)
        #
        # self.query_parameters_textbox = customtkinter.CTkTextbox(self.query_request_frame, height=150, width=250)
        # self.query_parameters_textbox.grid(row=1, column=1, padx=10, pady=10)

        # Config buttons
        self.config_buttons = customtkinter.CTkFrame(self.frame, corner_radius=0, fg_color="transparent")
        self.config_buttons.grid(row=4, column=0, padx=10, pady=10)

        self.config_buttons = customtkinter.CTkFrame(self.frame, corner_radius=0, fg_color="transparent")
        self._insert_widget(self.config_buttons)

        self.load_default_parameters = customtkinter.CTkButton(self.config_buttons,
                                                               text="Load Default",
                                                               command=self.__load_default_text)
        self.load_default_parameters.grid(row=0, column=0, padx=10, pady=0)

        self.update_custom_parameters = customtkinter.CTkButton(self.config_buttons,
                                                                text="Save Config",
                                                                command=self.__save_config_text)
        self.update_custom_parameters.grid(row=0, column=1, padx=10, pady=0)

        self.__load_config_text()

    def __load_config_text(self):
        self.__clear_config_text()

        token_settings = self.__file_handler.get_token_settings()
        query_settings = self.__file_handler.get_query_settings()

        self.token_header_textbox.insert("0.0", json.dumps(token_settings, indent=2))
        self.query_header_textbox.insert("0.0", json.dumps(query_settings, indent=2))

    def __load_default_text(self):
        msg = CTkMessagebox(title="Load Default Configuration?",
                            message="Are you sure you want to load the default configuration? "
                                    "(It will not overwrite existing data until you save.)",
                            icon="question",
                            option_1="Cancel",
                            option_2="Yes")
        if msg.get() != "Yes":
            return

        self.__file_handler.load_default_config()
        self.__load_config_text()

    def __clear_config_text(self):
        # Clears text from "0.0" -> first line.first column, to tkinter.END -> end of text
        self.token_header_textbox.delete("0.0", tkinter.END)
        self.query_header_textbox.delete("0.0", tkinter.END)

    def __save_config_text(self):
        msg = CTkMessagebox(title="Save Configuration?",
                            message="Are you sure you want to save the configuration?",
                            icon="question",
                            option_1="Cancel",
                            option_2="Yes")

        if msg.get() != "Yes":
            return

        token_settings = self.token_header_textbox.get("0.0", tkinter.END)
        query_settings = self.query_header_textbox.get("0.0", tkinter.END)

        is_successful = self.__file_handler.set_config(token_settings, query_settings)

        if not is_successful:
            # todo, change warning text to ERROR: json decoding error
            # todo: create popup window module to handle such cases

            print("JSON Decoding error")
            pass

        self.__load_config_text()
