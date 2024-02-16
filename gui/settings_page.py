import customtkinter
import file_handler


class SettingsPage:
    def __init__(self, parent, filehandler: file_handler.FileHandler):
        self.__parent = parent
        self.__filehandler = filehandler

        # Create settings frame
        self.settings_frame = customtkinter.CTkFrame(self.__parent, corner_radius=0, fg_color="transparent")
        self.settings_frame.grid_columnconfigure(0, weight=1)
        self.settings_text = customtkinter.CTkLabel(self.settings_frame, text="Settings Page",
                                                    font=customtkinter.CTkFont(size=20, weight="bold"))
        self.settings_text.grid(row=0, column=0, padx=20, pady=20)

        """ **************
        Secret Setter Frame 
        ************** """
        self.secret_setter_frame = customtkinter.CTkFrame(self.settings_frame, corner_radius=0, fg_color="transparent")
        self.secret_setter_frame.grid(row=1, column=0, padx=20, pady=20)

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
        self.style_frame = customtkinter.CTkFrame(self.settings_frame, corner_radius=0, fg_color="transparent")
        self.style_frame.grid(row=2, column=0, padx=10, pady=10)

        self.default_style_label = customtkinter.CTkLabel(self.style_frame, text="Process Mode")
        self.default_style_label.grid(row=0, column=0, padx=10, pady=10)

        # Todo set event to save default
        self.default_style_dropdown = customtkinter.CTkOptionMenu(self.style_frame,
                                                                  values=["Single-Photo", "Pair-Photo"],
                                                                  command=None)
        self.default_style_dropdown.grid(row=0, column=1, padx=10, pady=10)
        # Todo set it to the saved value

        # Process mode, sudoc, sudoc+cover, cover

        # Search by sudoc, title

    def __save_secrets_event(self):
        # get client id
        # get client secret
        # pass to filehandler

        print(f"client_id: {self.client_textbox.get()} client_secret: {self.secret_textbox.get()}")
        self.__filehandler.test_print("buzz")

        self.__filehandler.set_secrets(self.client_textbox.get(), self.secret_textbox.get())
