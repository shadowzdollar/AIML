import pandas as pd

pd.options.display.max_rows = 10

result = pd.read_csv("examples/ex6.csv")

print(result)

#reading the file in pieces

pd.read_csv("examples/ex6.csv", nrows=5)

#using also chunksize as the nrows

pd.read_csv("examples/ex6.csv", chunksize=1000)





