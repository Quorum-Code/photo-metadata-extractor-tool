import tkinter
import json
import customtkinter

import src.local_data.file_handler as fh
from src.gui.page import Page

class QueryProfilePage(Page):
    def __init__(self, parent, file_handler: fh.FileHandler):
        super().__init__(parent, "Query Profile")
        self.__file_handler = file_handler

        # ***********************
        # Wiki Link Frame
        # ***********************

        wiki_link = "Learn how to configure query profiles on the PMET wiki: ... "
        self.__wiki_frame = customtkinter.CTkFrame(self.frame, corner_radius=0, fg_color="transparent")
        self.__wiki_link_text = customtkinter.CTkTextbox(self.__wiki_frame, width=350, height=75)
        self.__wiki_link_text.insert("0.0", wiki_link)
        self.__wiki_link_text.configure(state="disabled")
        self.__wiki_link_text.grid(row=0, column=0, padx=self._padx, pady=self._pady)
        self._insert_widget(self.__wiki_frame)

        # ***********************
        # Query Profile Frame
        # ***********************

        self.__query_profile_frame = customtkinter.CTkScrollableFrame(self.frame, corner_radius=5, width=500, height=300)
        self.__query_profile_frame.grid_rowconfigure(6, weight=1)

        # Current Query Profile
        self.__profile_select_frame = customtkinter.CTkFrame(self.__query_profile_frame)
        self.__profile_select_label = customtkinter.CTkLabel(self.__profile_select_frame, text="Edit Profile", width=100)
        self.__profile_select_label.grid(row=0, column=0, padx=10, pady=10)
        self.__profile_select = customtkinter.CTkOptionMenu(self.__profile_select_frame)
        self.__profile_select.grid(row=0, column=1, padx=10, pady=10)
        self.__profile_select_frame.grid(row=0, column=0, padx=10)

        # Profile name
        self.__profile_name_frame = customtkinter.CTkFrame(self.__query_profile_frame)
        self.__profile_name_label = customtkinter.CTkLabel(self.__profile_name_frame, text="Profile Name", width=100)
        self.__profile_name_label.grid(row=0, column=0, padx=10, pady=10)
        self.__profile_name = customtkinter.CTkEntry(self.__profile_name_frame)
        self.__profile_name.grid(row=0, column=1, padx=10, pady=10)
        self.__profile_name_frame.grid(row=1, column=0, padx=10)

        # Search type
        self.__search_type_frame = customtkinter.CTkFrame(self.__query_profile_frame)
        self.__search_type_label = customtkinter.CTkLabel(self.__search_type_frame, text="Search Type", width=100)
        self.__search_type_label.grid(row=0, column=0, padx=10, pady=10)
        self.__search_type = customtkinter.CTkEntry(self.__search_type_frame)
        self.__search_type.grid(row=0, column=1, padx=10, pady=10)
        self.__search_type_frame.grid(row=2, column=0, padx=10)

        # Key dropdown
        self.__key_select_frame = customtkinter.CTkFrame(self.__query_profile_frame)
        self.__key_select_label = customtkinter.CTkLabel(self.__key_select_frame, text="Key Select", width=100)
        self.__key_select_label.grid(row=0, column=0, padx=10, pady=10)
        self.__key_select = customtkinter.CTkOptionMenu(self.__key_select_frame)
        self.__key_select.grid(row=0, column=1, padx=10, pady=10)
        self.__key_select_frame.grid(row=3, column=0, padx=10)

        # Key name
        self.__key_name_frame = customtkinter.CTkFrame(self.__query_profile_frame)
        self.__key_name_label = customtkinter.CTkLabel(self.__key_name_frame, text="Key Name", width=100)
        self.__key_name_label.grid(row=0, column=0, padx=10, pady=10)
        self.__key_name = customtkinter.CTkEntry(self.__key_name_frame)
        self.__key_name.grid(row=0, column=1, padx=10, pady=10)
        self.__key_name_frame.grid(row=4, column= 0, padx=10)

        # Text box list for map
        self.__key_map_frame = customtkinter.CTkFrame(self.__query_profile_frame)
        self.__key_map_label = customtkinter.CTkLabel(self.__key_map_frame, text="Key Map", width=100)
        self.__key_map_label.grid(row=0, column=0, padx=10, pady=10)
        self.__key_map = customtkinter.CTkTextbox(self.__key_map_frame, width=400)
        self.__key_map.grid(row=1, column=0, padx=10, pady=10)
        self.__key_map_frame.grid(row=5, column=0, padx=10)

        # Insert the query profile frame
        self._insert_widget(self.__query_profile_frame)

        # Save profile changes
        self.__save_button = customtkinter.CTkButton(self.frame, text="Save Profile")
        self._insert_widget(self.__save_button)

