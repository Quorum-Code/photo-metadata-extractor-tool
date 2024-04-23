import string
import time

# testing rule enforcement on main

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

# COL_NAMES = ["alpha", "beta"]
#
# with open("some.csv", mode='a', newline='') as file:
#     csvFile = csv.DictWriter(file, delimiter='|', fieldnames=COL_NAMES)
#
#     csvFile.writerows([{"alpha": "amazing", "beta": "bravo"}, {"alpha": "amazing", "beta": "bravo"}])

start = time.time()

thing = "This,  a thing, is a sentence with... puncuation!?"

print(thing)

whitespace_translator = str.maketrans("", "", string.whitespace)
punctuation_translator = str.maketrans("", "", string.punctuation)

thing = thing.translate(whitespace_translator).translate(punctuation_translator)

print(thing)

end = time.time()
print(end-start)
