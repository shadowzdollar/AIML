import numpy as np
import pandas as pd

data = pd.DataFrame(np.arange(12).reshape((3, 4)),

index=["Ohio", "Colorado", "New York"],

columns=["one", "two", "three", "four"])


#function

def transform(x):
    return x[:4].upper()

data.index.map(transform)

print(data.index.map(transform))

#discretization and binind



