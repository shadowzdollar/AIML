
#detecting and filtering outliers
import numpy as np
import pandas as pd

#random 50 ages
ages = np.random.randint(18, 85, size=50)

print(ages)

df = pd.DataFrame({'age': ages})


print(df)


#calculating the quatile range to remove the outliets

Q1 = df['age'].quantile(0.25)
Q3 = df['age'].quantile(0.75)

IQR = Q3 - Q1

filtered_df = df[(df['age'] >= Q1 - 1.5 * IQR) & (df['age'] <= Q3 + 1.5 * IQR)]

print(filtered_df)