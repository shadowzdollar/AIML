import numpy as np

import pandas as pd

values = pd.Series(['apple', 'orange', 'apple', 'apple'] * 2)
values.unique()
values.value_counts()


categories = pd.Series(['apple', 'orange']) 
codes = pd.array([0, 1, 0, 0, 0, 1, 0, 0])

cat = pd.Categorical.from_codes(codes, categories)

print(cat)