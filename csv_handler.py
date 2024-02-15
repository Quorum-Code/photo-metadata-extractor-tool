import csv
import time
import os
import file_handler as fh

csv_name = "some-file.csv"


class SuDocRecord:
    def __init__(self, raw_sudoc, sudoc, title, author):
        self.raw_sudoc = raw_sudoc
        self.sudoc = sudoc
        self.title = title
        self.author = author
        return

    def get_fields(self):
        return {self.raw_sudoc, self.sudoc, self.title, self.author}


class CSVDocument:
    def __init__(self, data_handler: fh.FileHandler, folder_path=""):
        self.__datahandler = data_handler

        # TODO: optional static path -> i.e. configing a folder to be the default path for csv files
        self.__file_path = ""
        self.__time_stamp_format = "%m-%d-%Y_%H.%M.%S"
        self.__file_extension = ".csv"
        self.__folder_name = "extractions"
        self.__folder_path = os.path.join(self.__datahandler.get_program_path(), self.__folder_name)

        # Create extractions folder if it doesn't already exist
        if not os.path.exists(self.__folder_path):
            os.mkdir(self.__folder_path)

        # check for static folder
        if folder_path != "" and os.path.exists(folder_path):
            self.__folder_path = folder_path
        # verify default folder exists
        else:
            return

        # generate document file
        # add column names
        return

    def write_row(self, sudoc_record: SuDocRecord):
        return

    def get_file_path(self) -> str:
        return self.__file_path

    def __generate_file(self):
        return

    def generate_file_name(self) -> str:
        time_stamp = time.strftime(self.__time_stamp_format, time.localtime())
        filename = "extraction_" + time_stamp + self.__file_extension

        return filename


if __name__ == "__main__":
    csv_file = CSVDocument(fh.FileHandler())
