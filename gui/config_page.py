import tkinter
import json
import customtkinter
from CTkMessagebox import CTkMessagebox

import file_handler as fh


class ConfigurationPage:
    def __init__(self, parent, file_handler: fh.FileHandler):
        self.__parent = parent
        self.__file_handler = file_handler
        self.popup_window = None

        # Create settings frame
        self.configuration_frame = customtkinter.CTkFrame(self.__parent, corner_radius=0, fg_color="transparent")
        self.configuration_frame.grid_columnconfigure(0, weight=1)
        self.configuration_text = customtkinter.CTkLabel(self.configuration_frame, text="Configuration Page",
                                                         font=customtkinter.CTkFont(size=20, weight="bold"))
        self.configuration_text.grid(row=0, column=0, padx=20, pady=20)

        # Config warning
        self.configuration_warning_frame = customtkinter.CTkFrame(self.configuration_frame,
                                                                  corner_radius=0,
                                                                  fg_color="transparent")
        self.configuration_warning_frame.grid(row=1, column=0, padx=10, pady=5)

        self.config_warning_text = customtkinter.CTkLabel(self.configuration_warning_frame,
                                                          text="WARNING: If you don't know what these settings mean, "
                                                               "don't change them.",
                                                          font=customtkinter.CTkFont(size=15, slant="italic"),
                                                          width=250)
        self.config_warning_text.grid(row=0, column=0)

        # Token Request config
        self.token_request_frame = customtkinter.CTkFrame(self.configuration_frame,
                                                          corner_radius=5)
        self.token_request_frame.grid(row=2, column=0, padx=10, pady=10)

        self.token_header_label = customtkinter.CTkLabel(self.token_request_frame, text="Token Request Header")
        self.token_header_label.grid(row=0, column=0)

        self.token_header_textbox = customtkinter.CTkTextbox(self.token_request_frame, height=150, width=250)
        self.token_header_textbox.grid(row=1, column=0, padx=10, pady=10)

        self.token_parameters_label = customtkinter.CTkLabel(self.token_request_frame, text="Token Request Paramenters")
        self.token_parameters_label.grid(row=0, column=1)

        self.token_parameters_textbox = customtkinter.CTkTextbox(self.token_request_frame, height=150, width=250)
        self.token_parameters_textbox.grid(row=1, column=1, padx=10, pady=10)

        # Query Request config
        self.query_request_frame = customtkinter.CTkFrame(self.configuration_frame,
                                                          corner_radius=5)
        self.query_request_frame.grid(row=3, column=0, padx=10, pady=10)

        self.query_header_label = customtkinter.CTkLabel(self.query_request_frame, text="Query Request Header")
        self.query_header_label.grid(row=0, column=0)

        self.query_header_textbox = customtkinter.CTkTextbox(self.query_request_frame, height=150, width=250)
        self.query_header_textbox.grid(row=1, column=0, padx=10, pady=10)

        self.query_parameters_label = customtkinter.CTkLabel(self.query_request_frame, text="Query Request Paramenters")
        self.query_parameters_label.grid(row=0, column=1)

        self.query_parameters_textbox = customtkinter.CTkTextbox(self.query_request_frame, height=150, width=250)
        self.query_parameters_textbox.grid(row=1, column=1, padx=10, pady=10)

        self.config_buttons = customtkinter.CTkFrame(self.configuration_frame, corner_radius=0, fg_color="transparent")
        self.config_buttons.grid(row=4, column=0, padx=10, pady=10)

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
        self.token_parameters_textbox.delete("0.0", tkinter.END)

        self.query_header_textbox.delete("0.0", tkinter.END)
        self.query_parameters_textbox.delete("0.0", tkinter.END)

    def __save_config_text(self):
        msg = CTkMessagebox(title="Save Configuration?",
                            message="Are you sure you want to save the configuration?",
                            icon="question",
                            option_1="Cancel",
                            option_2="Yes")

        if msg.get() != "Yes":
            return

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

        self.__load_config_text()
