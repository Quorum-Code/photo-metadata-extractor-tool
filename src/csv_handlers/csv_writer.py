import csv
import os
import time


def generate_filename() -> str:
    return CSVWriter.FILE_PREFIX + time.strftime(CSVWriter.TIME_FORMAT, time.localtime()) + CSVWriter.FILE_SUFFIX


class CSVWriter:
    FILE_PREFIX = "extraction_"
    TIME_FORMAT = "%m-%d-%Y_%H.%M.%S"
    DELIMITER = "|"
    FILE_SUFFIX = ".csv"

    def __init__(self, folder_path: str, file_name=""):
        self.__file_name: str = file_name
        if self.__file_name == "":
            self.__file_name = generate_filename()

        self.__folder_path: str = folder_path
        self.__path: str = self.__process_file_path()

        self.__ready: bool = (self.__path != "")
        self.__col_names: list[str]
        self.__rows: list[dict[str]]
        return

    def write_data(self, cols: list[str], rows: list[dict[str]]):
        if not self.__ready:
            print("unable to write data to csv")
            return

        with open(self.__path, mode='w', newline='') as file:
            csv_writer = csv.DictWriter(file, delimiter=CSVWriter.DELIMITER, fieldnames=cols)
            csv_writer.writeheader()
            csv_writer.writerows(rows)
        return

    def __process_file_path(self) -> str:
        if not os.path.exists(self.__folder_path) or not os.path.isdir(self.__folder_path):
            return ""

        # Generate file path
        path = os.path.join(self.__folder_path, self.__file_name)

        if os.path.exists(path):
            print("csv writer file already exists, generating new file")
            path = os.path.join(self.__folder_path,  self.__generate_filename())

        return path


def small_test():
    cw = CSVWriter("csv_writer_test.csv", "./")

    cols = ["cola", "colb"]
    rows = [
        {"cola": "aaaa", "colb": "b"},
        {"cola": "aaa", "colb": "bb"},
        {"cola": "aa", "colb": "bbb"}
    ]

    cw.write_data(cols, rows)
    return


def main():
    small_test()
    return


if __name__ == "__main__":
    main()
