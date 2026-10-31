import pandas as pd

# 1. Create a dictionary with some raw data
data = {
    "Name": ["Alice", "Bob", "Charlie"],
    "Age": [25, 30, 35],
    "City": ["New York", "London", "Paris"]
}

# 2. Convert the dictionary into a Pandas DataFrame (like an Excel table)
df = pd.DataFrame(data)

# 3. Print the data and the average age
print("--- Our Data Table ---")
print(df)
print("\n--- Average Age ---")
print(df["Age"].mean())
