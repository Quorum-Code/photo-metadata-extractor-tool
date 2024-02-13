import csv

csv_name = "some-file.csv"


def generate_file_name() -> str:
    return ""


class SuDocRecord:
    def __init__(self, raw_sudoc, fxd_sudoc, title, author):
        self.raw_sudoc = raw_sudoc
        self.fxd_sudoc = fxd_sudoc
        self.title = title
        self.author = author
        return

    def get_fields(self):
        return {self.raw_sudoc, self.fxd_sudoc, self.title, self.author}


def write_record(sudoc_record: SuDocRecord):

    with open(csv_name, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter='|')
        csv_writer.writerow(sudoc_record.get_fields())

    return


if __name__ == "__main__":
    write_record(SuDocRecord("alpha", "bravo", "charlie", "delta"))
