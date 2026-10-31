import pandas as pd
import sys

data = pd.read_csv("examples/ex5.csv")

print(data)

#rewriting the data back go the csv from data frame

data.to_csv("examples/out.csv")

#printing the csv as a text file not csv

data.to_csv(sys.stdout, sep="|")

#then replacing na by null

data.to_csv(sys.stdout, na_rep="NULL")



#skipping header and index

data.to_csv(sys.stdout, index=False, header=False)

