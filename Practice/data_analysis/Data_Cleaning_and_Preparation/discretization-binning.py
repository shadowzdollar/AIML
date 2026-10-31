import numpy as np
import pandas as pd

ages = [20, 22, 25, 27, 21, 23, 37, 31, 61, 45, 41, 32]


bins = [18, 25, 35, 60, 100]

age_categories = pd.cut(ages, bins)


print(age_categories)

#printing them into binaries of zeros and ones

print(age_categories.codes)



#real world example

# np.random.seed(42)
# # Generate 100 random annual spending values,
# # mostly between $500 and $1500, with some higher outliers
# annual_spending = pd.Series(np.random.normal(loc=1000, scale=300, size=100))
# # Ensure no negative spending and add a few high outliers
# annual_spending = annual_spending.apply(lambda x: max(50, x))
# annual_spending.iloc[0] = 5000  # A very high spender
# annual_spending.iloc[1] = 7500  # Another very high spender
# annual_spending.iloc[2] = 100   # A very low spender
# print("--- Original Annual Spending Data (first 10) ---")
# print(annual_spending.head(10))
# print(f"\nMin Spending: ${annual_spending.min():.2f}")
# print(f"Max Spending: ${annual_spending.max():.2f}")
# print(f"Mean Spending: ${annual_spending.mean():.2f}")


print(age_categories.categories)


print(age_categories.categories[0])


#counting the values

# pd.value_counts(age_categories)



#passing the arrauy of labels

group_names = ["Youth", "YoungAdults", "MiddleAged", "Senior"]

print(pd.cut(ages, bins, labels=group_names))

data = np.random.uniform(size=20)

print(pd.cut(data, 4, precision=2))