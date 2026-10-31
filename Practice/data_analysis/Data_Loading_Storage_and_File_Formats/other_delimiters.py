import pandas as pd

import csv

f = open("examples/ex7.csv")

reader = csv.reader(f)

#using for loop to read each line

for line in reader:
    print(line)

#then after closing the file

f.close()

#reading as the list

with open("examples/ex7.csv") as f:
    lines = list(csv.reader(f))

header, valuues = lines[0], lines[1:]


#dialect parameters specification

class my_dialect(csv.Dialect):
    lineterminator = "\n"
    delimeter = ";"
    quotechar = '"'
    quoting = csv.QUOTE_MINIMAL

#calling it in file reader

reader = csv.reader(f, dialect=my_dialect)

#partial dialect assignment

reader = csv.reader(f, delimeter="|")


