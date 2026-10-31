# Python for Data Analysis - Chapter 13: Getting Started
## Session 1: Environment Setup and Data Loading

---

## ⚡ Quick Start: Install & Import

If you haven't installed the required libraries yet, run:

```bash
pip install pandas numpy matplotlib seaborn
```

Then import them in Python:

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
```

**Style setup** (run once per session):
```python
sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (10, 6)
```

---

## 📥 Loading the Bitly Dataset

The book uses **Bitly data from 1.usa.gov** - a dataset of URL shortening logs.

### Option 1: If you have the dataset locally
```python
# Download from: 
# - oreilly.com (book's companion site)
# - GitHub: wesm/pydata-book (various datasets)

records = pd.read_csv('datasets/bitly/bitly-data.csv')
```

### Option 2: Using sample data (for now)
Since the dataset isn't included in your Resources folder, we'll create sample data that mimics the structure:

```python
import numpy as np
import pandas as pd

np.random.seed(42)
n_rows = 1000

# Create sample data similar to Bitly dataset structure
sample_data = {
    'a': np.random.choice(  # User agent string
        ['Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
         'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
         'GoogleMaps/RochesterNY',
         'Mozilla/5.0 (Linux; U; Android 2.2.2; en-us; LG-P9)'],
        size=n_rows
    ),
    'tz': np.random.choice(  # Time zone
        ['America/New_York', 'America/Denver', 'Europe/London',
         'Asia/Tokyo', ''],
        size=n_rows,
        p=[0.3, 0.15, 0.15, 0.1, 0.3]
    ),
    'c': np.random.choice(  # Referring channel
        ['indeed', 'facebook', 'twitter', 'direct'], 
        size=n_rows
    ),
}

records = pd.DataFrame(sample_data)
print(f"Loaded sample data: {records.shape[0]} rows, {len(records.columns)} columns")
```

---

## 🔍 Step 1: Explore the Data

### Check the structure
```python
# First 5 rows
print(records.head())

# Column names
print("Columns:", list(records.columns))

# Data types and non-null counts
print(records.dtypes)

# Total size
print(f"Rows: {records.shape[0]}, Columns: {records.shape[1]}")
```

### Expected output (with sample data):
```
   ...                    a                tz         c
0  ...  Mozilla/5.0 (Windows...  America/New_York  indeed
1  ...  Mozilla/5.0 (Macintosh...    America/Denver  facebook
2  ...  GoogleMaps/RochesterNY                    Europe/London  twitter
3  ...  Mozilla/5.0 (Linux;...                     Asia/Tokyo      direct
4  ...  Mozilla/5.0 (Windows...                    America/New_York  indeed

Columns: ['a', 'tz', 'c']
Rows: 1000, Columns: 3
```

---

## ⏰ Step 2: Time Zone Analysis (Section 13.2)

This is the **first analysis** in the chapter. We'll look at time zone distribution.

### 2.1 Basic Counts
```python
# Count occurrences of each time zone
tz_counts = records["tz"].value_counts()

print("Raw time zone counts:")
print(tz_counts)
```

### 2.2 Handling Missing Data
Real data has missing values. The book shows how to handle them:

```python
# Replace NaN values with "Missing"
clean_tz = records["tz"].fillna("Missing")

# Replace empty strings with "Unknown"  
clean_tz[clean_tz == ""] = "Unknown"

# Now count again
clean_tz_counts = clean_tz.value_counts()

print("\nCleaned time zone counts:")
print(clean_tz_counts)
```

### Why this matters:
- Original data had NaN (Not Available) and empty strings ""
- After cleaning, we have consistent categories: "Missing" and "Unknown"
- Makes visualization and analysis much cleaner

---

## 📊 Step 3: Basic Visualization

### 3.1 Bar Plot of Top Time Zones
```python
# Get top 10 time zones
top_10 = clean_tz_counts.head(10)

# Plot as bar chart
ax = top_10.plot(kind='bar', color='steelblue')

# Add titles and labels
plt.title("Top 10 Time Zones")
plt.xlabel("Time Zone")
plt.ylabel("Count")

# Rotate x-labels for readability
plt.xticks(rotation=45, ha='right')

# Adjust layout
plt.tight_layout()

# Show the plot
plt.show()
```

### 3.2 Using Seaborn for Enhanced Plots
The book uses seaborn for nicer visualizations:

```python
import seaborn as sns

# Create a nice horizontal bar plot
subset = top_10
sns.barplot(y=subset.index, x=subset.to_numpy())

# Add plot details
plt.title("Top Time Zones with Seaborn")
plt.tight_layout()

plt.show()
```

**Result**: Figure 13-1 from the book - a clean horizontal bar chart showing the top time zones.

---

## 🖥️ Step 4: Operating System Analysis (Section 13.3)

### 4.1 Filtering by Operating System
We can break down the analysis by whether users are on Windows or not:

```python
# Filter to rows where we have agent string data
cframe = records[records["a"].notna()].copy()

# Create OS column: "Windows" if agent string contains "Windows", else "Not Windows"
cframe["os"] = np.where(
    cframe["a"].str.contains("Windows"),
    "Windows", "Not Windows"
)

print("OS distribution:")
print(cframe["os"].value_counts())
```

### 4.2 Grouping by Time Zone and OS
```python
# Group by both time zone AND operating system
by_tz_os = cframe.groupby(["tz", "os"])

# Get counts for each group
agg_counts = by_tz_os.size().unstack().fillna(0)

print("\nCounts by time zone and OS:")
print(agg_counts.head())
```

### 4.3 Selecting Top Time Zones
```python
# Sort by total count (across both OS types)
indexer = agg_counts.sum("columns").argsort()

# Select the top 10 time zones (largest values)
count_subset = agg_counts.take(indexer[-10:])

print("\nTop 10 time zones by OS:")
print(count_subset)
```

### 4.4 Visualizing Windows vs Non-Windows
```python
# Plot the top 10 time zones grouped by OS
count_subset.plot(kind='bar', figsize=(10, 6))
plt.title("Top 10 Time Zones by Operating System")
plt.xlabel("Time Zone")
plt.ylabel("Count")
plt.legend(["Not Windows", "Windows"])
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()
```

---

## 📝 Key Takeaways from Session 1

| Concept | Method | Purpose |
|---------|--------|---------|
| Load data | `pd.read_csv()` | Read dataset into DataFrame |
| Summarize | `value_counts()` | Count categorical occurrences |
| Handle NaN | `.fillna("Missing")` | Replace missing values |
| Handle empty | `== ""` assignment | Replace empty strings |
| Filter data | `.notna()` / `.isna()` | Select rows with/without missing data |
| Conditional column | `np.where()` | Create new column based on condition |
| Group & aggregate | `.groupby().size().unstack()` | Cross-tabulation |
| Visualize | `.plot(kind='bar')` / `sns.barplot()` | Create charts |

---

## 🛠️ Your Turn: Practice Exercise

Try these steps with your sample data (or the real dataset when you have it):

1. **Run the code above** and observe the outputs
2. **Modify the data**: Change the `np.random.seed()` value and observe how the counts change
3. **Add a new column**: Create a "browser" column by extracting the browser name from the agent string `a`
4. **Create a pie chart**: Instead of a bar chart, plot the time zones as a pie chart

### Exercise Template:
```python
# 1. Load your data
# records = pd.read_csv('your-data.csv')

# 2. Time zone counts
tz_counts = records["tz"].value_counts()
print("Raw counts:", tz_counts.head())

# 3. Clean missing data
clean_tz = records["tz"].fillna("Missing")
clean_tz[clean_tz == ""] = "Unknown"
clean_counts = clean_tz.value_counts()
print("Cleaned counts:", clean_counts.head())

# 4. Plot
clean_counts.head(10).plot(kind='bar')
plt.title("Top Time Zones")
plt.show()
```

---

## ❓ Need Help?

If you get stuck or have questions about:
- Loading your specific dataset
- Understanding any of the code
- Modifying the exercises
- Visualization customization

Just ask! I'm here to help you work through Chapter 13 step-by-step.