import customtkinter
from src.gui.page import Page
import pandas as pd
import tksheet
import os
from PIL import Image, ExifTags
from customtkinter import filedialog
from CTkMessagebox import CTkMessagebox


class ProcessExtractedDataPage(Page):
    def __init__(self, parent: customtkinter.CTk, settings_win):
        super().__init__(parent, title="OCR Extraction Processing Page")
        self.__file_icon_local_path = "icons\\folder-icon.png"
        self.__file_icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), self.__file_icon_local_path)
        self.__file_icon = customtkinter.CTkImage(Image.open(self.__file_icon_path), size=(24, 24))

        self.__save_icon_local_path = "icons\\save_icon.jpg"
        self.__save_icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), self.__save_icon_local_path)
        self.__save_icon = customtkinter.CTkImage(Image.open(self.__save_icon_path), size=(24, 24))

        self.datapath = ''
        self.curr_sel_img_pth = ''
        self.data = ''
        self.__extraction_processing_frame = customtkinter.CTkFrame(self.frame, corner_radius=0,
                                                                    fg_color="transparent", bg_color="transparent")
        self.__extraction_processing_frame.grid_columnconfigure(0, weight=1)
        self.__settings_win = settings_win

        # TITLE
        self.__title_text = customtkinter.CTkLabel(self.frame, text="OCR Extraction Processing Page",
                                                   font=self.title_font)
        self._insert_widget(self.__title_text)

        #Extracted data csv selector box
        self.curr_extract_sel_frame = customtkinter.CTkFrame(self.frame, corner_radius=0)
        self.curr_extract_sel_frame.grid(row=1, column=0, padx=5, pady=5)

        self.curr_extract = customtkinter.CTkLabel(self.curr_extract_sel_frame,
                                                   text="Current Extract", width=80)
        self.curr_extract.grid(row=0, column=0, padx=5, pady=5)

        self.select_extracted_data_csv_button = customtkinter.CTkButton(self.curr_extract_sel_frame,
                                                                        text="",
                                                                        image=self.__file_icon,
                                                                        height=10,
                                                                        width=10,
                                                                        border_spacing=0,
                                                                        corner_radius=0,
                                                                        fg_color="transparent",
                                                                        command=self.__ask_extracted_data_csv)

        self.select_extracted_data_csv_button.grid(row=0, column=1, padx=5, pady=5)

        self.curr_extract_path = customtkinter.CTkLabel(self.curr_extract_sel_frame,
                                                        text=self.datapath,
                                                        anchor="w",
                                                        width=300)
        self.curr_extract_path.grid(row=0, column=2, padx=5, pady=5)

        #Currently selected image box

        self.curr_extract_sel_img_fr = customtkinter.CTkFrame(self.frame, corner_radius=0)
        self.curr_extract_sel_img_fr.grid(row=1, column=1, padx=0, pady=5)

        self.curr_sel_img_label_frame = customtkinter.CTkLabel(self.curr_extract_sel_img_fr,
                                                               text="Currently Selected Image: ", width=20,
                                                               fg_color='transparent')

        self.curr_sel_img_label_frame.grid(row=0, column=0, padx=0, pady=5)

        self.curr_sel_img_border = customtkinter.CTkFrame(self.frame, corner_radius=0, width=470, height=470)
        self.curr_sel_img_border.grid(row=2, column=1, padx=0, pady=5)

        self.curr_sel_img_frame = customtkinter.CTkLabel(self.curr_sel_img_border, text="", corner_radius=0,
                                                         fg_color="transparent",
                                                         width=470, height=470)
        self.curr_sel_img_frame.grid(row=2, column=1, padx=0, pady=5)

        self.frame.grid_columnconfigure((0, 1, 2), pad=0, weight=1)

        ### INITIALIZE SHEET
        self.sheet = tksheet.Sheet(self.frame, page_up_down_select_row=False,
                                   height=750,
                                   width=1200,
                                   theme="black",
                                   empty_vertical=20,
                                   empty_horizontal=20,
                                   horizontal_grid_to_end_of_window=True,
                                   vertical_grid_to_end_of_window=True,
                                   #show_vertical_grid=True,
                                   #show_horizontal_grid=True,
                                   outline_thickness=2,
                                   outline_color='grey',
                                   )

        if self.__settings_win.output_type == 'Pair-Photo':
            self.sheet.headers(self.get_data_column_headers('ocr_editing_pair'))
            self.sheet.readonly_columns(columns=[0, 3, 4, 5, 6, 7, 8])
        elif self.__settings_win.output_type == 'Single-Photo':
            self.sheet.headers(self.get_data_column_headers('ocr_editing_single'))
            self.sheet.readonly_columns(columns=[0, 2, 3, 4, 5])

        self.sheet.headers(self.get_data_column_headers('ocr_editing_pair'))
        self.sheet.grid(row=2, column=0, padx=0)

        self.sheet.enable_bindings('all')

        self.sheet.disable_bindings('rc_delete_column', 'rc_insert_column')

        self.sheet.enable_bindings("rc_select", "rc_insert_row", "rc_delete_row")

        self.sheet.extra_bindings("cell_select", self.event_img_cell_select)

        #### Save sheet button

        self.save_button_frame = customtkinter.CTkFrame(self.frame, corner_radius=0, height=40)
        self.save_button_frame.grid(row=3, column=0, padx=5, pady=5)

        self.save_button_label = customtkinter.CTkLabel(self.save_button_frame,
                                                        text="Save Sheet", fg_color='transparent')
        self.save_button_label.grid(row=0, column=0, padx=5, pady=5)

        self.save_button = customtkinter.CTkButton(self.save_button_frame,
                                                   text="",
                                                   image=self.__save_icon,
                                                   height=10,
                                                   width=10,
                                                   border_spacing=0,
                                                   corner_radius=0,
                                                   fg_color="transparent",
                                                   bg_color="transparent",
                                                   command=self.save_sheet_changes)

        self.save_button.grid(row=0, column=1, padx=5, pady=5)

    def __ask_extracted_data_csv(self):
        self.datapath = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        self.datapath = self.load_extracted_data()
        if self.datapath != "":
            self.update_curr_extract_path_text(self.datapath)

    def update_curr_extract_path_text(self, text):
        self.curr_extract_path.configure(text=text)

    def get_data_column_headers(self, header_group):
        if header_group == 'complete_pair':
            return ['ID', 'Title',
                    'SuDoc', 'Publication Year',
                    'Path', 'Error Code', 'Query Status',
                    'Sudoc Image', 'Title Image',
                    'Image 1 Path', 'Image 2 Path',
                    'Image 1 Ext', 'Image 2 Ext']
        elif header_group == 'complete_single':
            return ['ID', 'extracted_text',
                    'Publication Year', 'Error Code', 'Query Status',
                    'Image 1 Path']
        elif header_group == 'ocr_editing_pair':
            return ['ID', 'Title', 'SuDoc',
                    'Sudoc Image', 'Title Image',
                    'Image 1 Path', 'Image 2 Path',
                    'Image 1 Ext', 'Image 2 Ext']
        elif header_group == 'ocr_editing_single':
            return ['ID', 'extracted_text',
                    'Image 1 Path']

    def try_catch_data_load(func):
        def wrap(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
            except ValueError:
                CTkMessagebox(title="ERROR", message="Invalid Data File", icon='cancel')
                result = ''
            return result

        return wrap

    def event_img_cell_select(self, event):
        if (self.__settings_win.output_type == "Single-Photo" and self.sheet.headers() == self.get_data_column_headers(
                "ocr_editing_pair")
                or self.__settings_win.output_type == "Pair-Photo" and self.sheet.headers() ==
                self.get_data_column_headers("ocr_editing_single")):
            pass
        else:
            cell_value = self.sheet.get_cell_data(event['selected'].row, event['selected'].column)
            if (self.__settings_win.output_type == "Pair-Photo" and event['selected'].column in [3, 4, 5, 6]
                    and cell_value == cell_value and cell_value != ""):
                self.curr_sel_img_pth = cell_value
                self.update_curr_selected_img(self.curr_sel_img_pth)

            elif self.__settings_win.output_type == "Single-Photo" and event['selected'].column in [
                2] and cell_value == cell_value and cell_value != "":
                self.curr_sel_img_pth = cell_value
                self.update_curr_selected_img(self.curr_sel_img_pth)

    def update_curr_selected_img(self, path):
        img = Image.open(path)
        '''
        if img.width > img.height:
            img = img.rotate(270)
        '''

        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break

        exif = img._getexif()

        if exif != None and orientation in exif:

            if exif[orientation] == 3:
                img = img.rotate(180, expand=True)
            elif exif[orientation] == 6:
                img = img.rotate(270, expand=True)
            elif exif[orientation] == 8:
                img = img.rotate(90, expand=True)

        curr_img = customtkinter.CTkImage(img, size=(450, 450))
        self.curr_sel_img_frame.configure(image=curr_img, text='', padx=0)
        self.update_curr_selected_img_pth(os.path.basename(path))

    def update_curr_selected_img_pth(self, pth):
        text = "Currently Selected Image: " + pth
        self.curr_sel_img_label_frame.configure(text=text)

    def save_sheet_changes(self):
        if self.__settings_win.output_type == 'Pair-Photo' and self.sheet.headers() == self.get_data_column_headers(
                "ocr_editing_pair"):
            orig_data = pd.read_csv(self.datapath,
                                    usecols=self.get_data_column_headers('complete_pair'))
            new_df = pd.DataFrame(self.sheet.data,
                                  columns=self.get_data_column_headers("ocr_editing_pair"))
            conc_df = pd.merge(orig_data[['ID',
                                          'Publication Year',
                                          'Path', 'Error Code', 'Query Status',
                                          'Sudoc Image', 'Title Image',
                                          'Image 1 Path', 'Image 2 Path',
                                          'Image 1 Ext', 'Image 2 Ext']], new_df[['ID', 'SuDoc', 'Title']],
                               how="left", on=['ID'])

            new_rows = new_df[new_df.ID == '']
            conc_df = pd.concat([conc_df, new_rows])
            conc_df = conc_df.reset_index()
            conc_df['ID'] = conc_df.index
            conc_df = conc_df[self.get_data_column_headers('complete_pair')]
            conc_df.to_csv(self.datapath, index=False)

        elif self.__settings_win.output_type == 'Single-Photo' and self.sheet.headers() == self.get_data_column_headers(
                "ocr_editing_single"):
            orig_data = pd.read_csv(self.datapath,
                                    usecols=self.get_data_column_headers('complete_single'))
            new_df = pd.DataFrame(self.sheet.data,
                                  columns=self.get_data_column_headers("ocr_editing_single"))
            conc_df = pd.merge(orig_data[['ID',
                                          'Publication Year',
                                          'Error Code', 'Query Status',
                                          'Image 1 Path']], new_df[['ID', 'extracted_text']],
                               how="left", on=['ID'])

            new_rows = new_df[new_df.ID == '']
            conc_df = pd.concat([conc_df, new_rows])
            conc_df = conc_df.reset_index()
            conc_df['ID'] = conc_df.index
            conc_df = conc_df[self.get_data_column_headers('complete_single')]
            conc_df.to_csv(self.datapath, index=False)

        else:
            CTkMessagebox(title="ERROR",
                          message="Settings selection and loaded data processing type(pair/single image) /"
                                  "do not match!!!", icon='cancel')
            return

        self.load_extracted_data()

    @try_catch_data_load
    def load_extracted_data(self):
        if self.__settings_win.output_type == 'Pair-Photo':
            self.sheet.headers(self.get_data_column_headers('ocr_editing_pair'))
            self.data = pd.read_csv(self.datapath, index_col=False,
                                    usecols=self.get_data_column_headers('ocr_editing_pair'),
                                    keep_default_na=False)
            self.sheet.readonly_columns(columns=[1, 2], readonly=False)
            self.sheet.readonly_columns(columns=[0, 3, 4, 5, 6, 7, 8])
        elif self.__settings_win.output_type == 'Single-Photo':
            self.sheet.headers(self.get_data_column_headers('ocr_editing_single'))
            self.data = pd.read_csv(self.datapath, index_col=False,
                                    usecols=self.get_data_column_headers('ocr_editing_single'),
                                    keep_default_na=False)
            self.sheet.readonly_columns(columns=[1], readonly=False)
            self.sheet.readonly_columns(columns=[0, 2, 3, 4, 5])

        self.sheet.set_sheet_data(self.data.to_numpy().tolist())
        self.sheet.extra_bindings("cell_select", self.event_img_cell_select)
        self.sheet.grid(padx=0)
        return self.datapath
