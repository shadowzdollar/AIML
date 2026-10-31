import pandas as pd

obj = pd.Series(["c", "a", "d", "a", "a", "b", "b", "c", "c"])


uniques = obj.unique()

print(uniques)

#counting the object values

print(obj.value_counts())