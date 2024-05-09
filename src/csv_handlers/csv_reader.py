import csv
import os


class CSVReader:
    DELIMITER = "|"

    def __init__(self, path):
        self.__path: str = path
        self.__col_names: list[str] = []
        self.__rows: list = []

        self.__read_data()
        return

    def __read_data(self):
        if self.__path == "":
            return

        if not os.path.exists(self.__path):
            return

        with open(self.__path, mode='r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='|')
            for row in csv_reader:
                self.__rows.append(row)

        self.__col_names = self.__rows[0]
        self.__rows = self.__rows[1:]
        print(f"d: {self.__rows}")

        return

    def get_data(self) -> list[dict]:
        return self.__rows

    def get_col_names(self) -> list[str]:
        return self.__col_names

    def get_query_terms(self) -> list[str]:
        return self.get_col(0)

    def get_col(self, index: int) -> list[str]:
        col_data: list[str] = []

        for i in range(len(self.__rows)):
            col_data.insert(i, self.__rows[i][index])

        return col_data


def main():
    path = "./extractions/extraction_02-18-2024_13.46.13.csv"
    cr = CSVReader(path)
    print(cr.get_col_names())
    print(cr.get_data())
    return


if __name__ == "__main__":
    main()
