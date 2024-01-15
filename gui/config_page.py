import customtkinter


class ConfigurationPage:
    def __init__(self, parent):
        self.__parent = parent

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

        self.token_header_textbox = customtkinter.CTkTextbox(self.token_request_frame, height=150)
        self.token_header_textbox.grid(row=1, column=0, padx=10, pady=10)

        self.token_parameters_label = customtkinter.CTkLabel(self.token_request_frame, text="Token Request Paramenters")
        self.token_parameters_label.grid(row=0, column=1)

        self.token_parameters_textbox = customtkinter.CTkTextbox(self.token_request_frame, height=150)
        self.token_parameters_textbox.grid(row=1, column=1, padx=10, pady=10)

        # Query Request config
        self.query_request_frame = customtkinter.CTkFrame(self.configuration_frame,
                                                          corner_radius=5)
        self.query_request_frame.grid(row=3, column=0, padx=10, pady=10)

        self.query_header_label = customtkinter.CTkLabel(self.query_request_frame, text="Query Request Header")
        self.query_header_label.grid(row=0, column=0)

        self.query_header_textbox = customtkinter.CTkTextbox(self.query_request_frame, height=150)
        self.query_header_textbox.grid(row=1, column=0, padx=10, pady=10)

        self.query_parameters_label = customtkinter.CTkLabel(self.query_request_frame, text="Query Request Paramenters")
        self.query_parameters_label.grid(row=0, column=1)

        self.query_parameters_textbox = customtkinter.CTkTextbox(self.query_request_frame, height=150)
        self.query_parameters_textbox.grid(row=1, column=1, padx=10, pady=10)

        self.config_buttons = customtkinter.CTkFrame(self.configuration_frame,
                                                     corner_radius=0,
                                                     fg_color="transparent")
        self.config_buttons.grid(row=4, column=0, padx=10, pady=10)

        self.load_default_parameters = customtkinter.CTkButton(self.config_buttons, text="Load Default")
        self.load_default_parameters.grid(row=0, column=0, padx=10, pady=0)

        self.update_custom_parameters = customtkinter.CTkButton(self.config_buttons, text="Save Config")
        self.update_custom_parameters.grid(row=0, column=1, padx=10, pady=0)