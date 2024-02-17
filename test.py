import csv
import pandas

# with open("some.csv", mode='r') as file:
#     csvFile = csv.DictReader(file, delimiter='|')
#     for name in csv.DictReader.reader:
#         print(name)

# csvFile = pandas.read_csv("some.csv", sep="|")
#
# thing = csvFile.loc[0]
# print(f"This is: {thing['cola']}")
#
# csvFile.to_csv("some.csv", sep="|")

COL_NAMES = ["alpha", "beta"]

with open("some.csv", mode='a', newline='') as file:
    csvFile = csv.DictWriter(file, delimiter='|', fieldnames=COL_NAMES)

    csvFile.writerows([{"alpha": "amazing", "beta": "bravo"}, {"alpha": "amazing", "beta": "bravo"}])
