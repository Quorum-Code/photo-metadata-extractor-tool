import tkinter
import json
import customtkinter
from gui.page import Page
import file_handler as fh


class ConfigurationPage(Page):
    def __init__(self, parent, file_handler: fh.FileHandler):
        super().__init__(parent, "Configuration")

        self.__file_handler = file_handler
        self.popup_window = None

        # Token Request config
        self.token_request_frame = customtkinter.CTkFrame(self.frame, corner_radius=5)
        self._insert_widget(self.token_request_frame)

        self.token_header_label = customtkinter.CTkLabel(self.token_request_frame, text="Token Request Header")
        self.token_header_label.grid(row=0, column=0)

        self.token_header_textbox = customtkinter.CTkTextbox(self.token_request_frame, height=150, width=250)
        self.token_header_textbox.grid(row=1, column=0, padx=10, pady=10)

        self.token_parameters_label = customtkinter.CTkLabel(self.token_request_frame, text="Token Request Paramenters")
        self.token_parameters_label.grid(row=0, column=1)

        self.token_parameters_textbox = customtkinter.CTkTextbox(self.token_request_frame, height=150, width=250)
        self.token_parameters_textbox.grid(row=1, column=1, padx=10, pady=10)

        # Query Request config
        self.query_request_frame = customtkinter.CTkFrame(self.frame, corner_radius=5)
        self._insert_widget(self.query_request_frame)

        self.query_header_label = customtkinter.CTkLabel(self.query_request_frame, text="Query Request Header")
        self.query_header_label.grid(row=0, column=0)

        self.query_header_textbox = customtkinter.CTkTextbox(self.query_request_frame, height=150, width=250)
        self.query_header_textbox.grid(row=1, column=0, padx=10, pady=10)

        self.query_parameters_label = customtkinter.CTkLabel(self.query_request_frame, text="Query Request Paramenters")
        self.query_parameters_label.grid(row=0, column=1)

        self.query_parameters_textbox = customtkinter.CTkTextbox(self.query_request_frame, height=150, width=250)
        self.query_parameters_textbox.grid(row=1, column=1, padx=10, pady=10)

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

        token_headers = self.__file_handler.get_token_headers()
        token_body = self.__file_handler.get_token_body()
        query_headers = self.__file_handler.get_query_headers()
        query_parameters = self.__file_handler.get_query_parameters()

        self.token_header_textbox.insert("0.0", json.dumps(token_headers, indent=2))
        self.token_parameters_textbox.insert("0.0", json.dumps(token_body, indent=2))
        self.query_header_textbox.insert("0.0", json.dumps(query_headers, indent=2))
        self.query_parameters_textbox.insert("0.0", json.dumps(query_parameters, indent=2))

    def __load_default_text(self):
        self.__file_handler.load_default_config()
        self.__load_config_text()

    def __clear_config_text(self):
        # Clears text from "0.0" -> first line.first column, to tkinter.END -> end of text
        self.token_header_textbox.delete("0.0", tkinter.END)
        self.token_parameters_textbox.delete("0.0", tkinter.END)

        self.query_header_textbox.delete("0.0", tkinter.END)
        self.query_parameters_textbox.delete("0.0", tkinter.END)

    def __save_config_text(self):
        token_headers = self.token_header_textbox.get("0.0", tkinter.END)
        token_body = self.token_parameters_textbox.get("0.0", tkinter.END)
        query_headers = self.query_header_textbox.get("0.0", tkinter.END)
        query_parameters = self.query_parameters_textbox.get("0.0", tkinter.END)

        is_successful = self.__file_handler.set_config(token_headers, token_body, query_headers, query_parameters)

        if not is_successful:
            # todo, change warning text to ERROR: json decoding error
            # todo: create popup window module to handle such cases

            print("JSON Decoding error")
            pass
