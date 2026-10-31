import numpy as np 
import pandas as pd

data = pd.Series([10, 25, 30, 45])

binned_data = pd.cut(data, bins=2, lables=['Low', 'high'])


print("Binned Data:\n", binned_data)
print("\nBinned Data COdes(.cat.codes):\n", binned_data.cat.codes)