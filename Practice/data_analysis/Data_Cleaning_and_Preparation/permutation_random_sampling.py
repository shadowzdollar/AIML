import numpy as np
import pandas as pd


df = pd.DataFrame(np.arange(5 * 7).reshape((5, 7)))


print(df)

sampler = np.random.permutation(5)


print(sampler)

#re-ordering the df uisng sampler

df.take(sampler)


column_sampler = np.random.permutation(7)

print(column_sampler)




