import numpy as np
import pandas as pd

ages = [
  18, 24, 31, 45, 29, 62, 37, 19, 53, 22,
  40, 27, 33, 58, 21, 65, 35, 48, 26, 30,
  52, 19, 44, 28, 61, 38, 23, 50, 36, 42,
  25, 59, 32, 47, 20, 64, 39, 55, 22, 41,
  34, 49, 18, 57, 26, 43, 51, 30, 60, 28
]

bins = [10, 30, 40, 50, 100]

print(pd.cut(ages, bins))


#labeling theim

lables_names = ["Youth", "YoungAdult", "MiddleAged", "Senior"]

print(pd.cut(ages, bins, lables=lables_names))