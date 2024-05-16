import csv
import time
import os
import src.local_data.file_handler as fh

FOLDER_NAME = "extractions"
FILE_PREFIX = "extraction_"
TIME_FORMAT = "%m-%d-%Y_%H.%M.%S"
DELIMITER = "|"
FILE_SUFFIX = ".csv"

COL_NAMES = ["SuDoc", "Status", "FilteredSuDoc", "GovernmentNumber", "Title", "Author", "PublicationDate"]


def generate_filename() -> str:
    return FILE_PREFIX + time.strftime(TIME_FORMAT, time.localtime()) + FILE_SUFFIX


class SuDocRecord:
    def __init__(self, sudoc: str, status: str, filtered_sudoc: str, gov_num: str, title: str,
                 author: str, publication_date: str):
        self.sudoc = sudoc
        self.status = status
        self.filtered_sudoc = filtered_sudoc
        self.gov_num = gov_num
        self.title = title
        self.author = author
        self.publication_date = publication_date

    def get_dict(self) -> dict[str]:
        record_dict = {COL_NAMES[0]: f"{self.sudoc}",
                       COL_NAMES[1]: f"{self.status}",
                       COL_NAMES[2]: f"{self.filtered_sudoc}",
                       COL_NAMES[3]: f"{self.gov_num}",
                       COL_NAMES[4]: f"{self.title}",
                       COL_NAMES[5]: f"{self.author}",
                       COL_NAMES[6]: f"{self.publication_date}"}
        return record_dict


class CSVDocument:
    def __init__(self, data_handler: fh.FileHandler, folder_path="", file_name="", file_path="", read_only=True):
        self.__datahandler = data_handler
        self.__file_contents: list[dict] = []
        self.__file_rows: list[list[str]] = []
        self.__file_name = file_name
        self.__file_path = file_path
        self.__folder_path = folder_path
        self.__read_only = read_only

        if file_path == "":
            if self.__folder_path == "":
                self.__folder_path = os.path.join(self.__datahandler.get_program_path(), FOLDER_NAME)
                print(self.__folder_path)
            # Try Load filename
            if self.__file_name != "":
                # Check that file exists
                self.__file_path = os.path.join(self.__folder_path, self.__file_name)
                if not os.path.exists(self.__file_path):
                    print("File or folder does not exist... generating a new file instead")
                    self.__file_name = ""
            else:
                self.__file_name = generate_filename()
                self.__file_path = os.path.join(self.__folder_path, self.__file_name)
                open(self.__file_path, 'w')

        # Check if file has column names
        col_names = []
        with open(self.__file_path, mode='r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='|')
            for row in csv_reader:
                self.__file_rows.append(row)

        # Check if file is not
        # if len(col_names) != 0 and col_names != COL_NAMES:
        #     self.__file_path = os.path.join(self.__folder_path, generate_filename())
        #     open(self.__file_path, 'w')
        #     print("ERROR: FILE CONTAINS ALTERNATE DATA... closing document to avoid overwriting data.")
        #     print(f"{col_names}")

        # if len(col_names) <= 1:
        #     # Insert column names
        #     with open(self.__file_path, mode='w', newline='') as file:
        #         csv_writer = csv.DictWriter(file, delimiter='|', fieldnames=COL_NAMES)
        #         csv_writer.writeheader()
        #     return
        #
        # # Load dictionary with csv data
        # with open(self.__file_path, mode='r') as file:
        #     csv_file = csv.DictReader(file, delimiter=DELIMITER)
        #     for row in csv_file:
        #         self.__file_contents.append(row)

        # TODO: optional static path -> i.e. configing a folder to be the default path for csv files
        # self.__file_path = ""
        # self.__time_stamp_format = "%m-%d-%Y_%H.%M.%S"
        # self.__file_extension = ".csv"
        # self.__delimiter = '|'
        # self.__column_names = ["RawSuDoc", "SuDoc", "Title", "Author", "PublicationDate"]
        # self.__folder_name = "extractions"
        # self.__folder_path = os.path.join(self.__datahandler.get_program_path(), self.__folder_name)
        #
        # # Create extractions folder if it doesn't already exist
        # if not os.path.exists(self.__folder_path):
        #     os.mkdir(self.__folder_path)
        #
        # # check for static folder
        # if folder_path != "" and os.path.exists(folder_path):
        #     self.__folder_path = folder_path
        # # verify default folder exists
        # elif not os.path.exists(self.__folder_path):
        #     print("ERROR: CSV file path does not exist")
        #     return
        #
        # print(self.__folder_path)
        #
        # # generate document file
        # with open(os.path.join(self.__folder_path, self.generate_file_name()), 'w', newline='') as csvfile:
        #     csv_writer = csv.writer(csvfile, delimiter=self.__delimiter, quotechar=' ', quoting=csv.QUOTE_MINIMAL)
        #     csv_writer.writerow(self.__column_names)
        #     csv_writer.writerow(['r', 's', 't', 'a', 'pd'])
        return

    def add_row(self, row: dict):
        if self.__read_only:
            print("cant add to a read only file")
            return

        self.__file_contents.append(row)
        self.__write_contents()

    def get_all_sudocs(self) -> list[str]:
        sudocs = []

        if len(self.__file_rows) <= 1:
            return []

        sudoc_index = -1
        for i in range(len(self.__file_rows[0])):
            if self.__file_rows[0][i] == "SuDoc":
                sudoc_index = i
                break

        if sudoc_index == -1:
            return []

        for row in self.__file_rows:
            sudocs.append(row[sudoc_index])

        return sudocs

    def __write_contents(self):
        if self.__read_only:
            print("cant write to a read only file")
            return

        with open(self.__file_path, mode='w', newline='') as file:
            csv_writer = csv.DictWriter(file, delimiter=DELIMITER, fieldnames=COL_NAMES)
            csv_writer.writeheader()
            csv_writer.writerows(self.__file_contents)

    def write_row(self, sudoc_record: SuDocRecord):
        if self.__read_only:
            print("cant write a row to a read only file")
            return
        return

    def write_contents_to_file(self):
        if self.__read_only:
            return

        with open(self.__file_path, mode='w', newline='') as file:
            csv_writer = csv.DictWriter(file, delimiter=DELIMITER, fieldnames=COL_NAMES)
            csv_writer.writeheader()
            csv_writer.writerows(self.__file_contents)

    def get_file_path(self) -> str:
        return self.__file_path

    def __generate_file(self):
        return

    def __generate_file_name(self) -> str:
        time_stamp = time.strftime(self.__time_stamp_format, time.localtime())
        filename = "extraction_" + time_stamp + self.__file_extension

        return filename


# if __name__ == "__main__":
#     start_time = time.time()
#     csvfile = CSVDocument(fh.FileHandler(), file_name="extraction_02-18-2024_13.46.13.csv")
#     # csvfile.add_row({"SuDoc": "su", "FilteredSuDoc": "fs", "Title": "ti", "Author": "au", "PublicationDate": "pd", "ImagePath": ""})
#     print(csvfile.get_all_sudocs())
#     end_time = time.time()
#
#     print(f"Total time: {end_time - start_time}")
