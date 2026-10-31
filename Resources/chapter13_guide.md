# Python for Data Analysis - Chapter 13: Data Analysis Examples
# Last Chapter Learning Guide

## Chapter Overview
Chapter 13 focuses on practical data analysis using real-world Bitly data from 1.usa.gov. The chapter demonstrates end-to-end data analysis workflows using pandas, matplotlib, seaborn, and numpy.

## Key Topics Covered

### 13.1 Bitly Data from 1.USA.gov (Page 427)
- Loading CSV data with pandas
- Examining data structure and columns
- Working with time zone data
- Filtering and cleaning data

### 13.2 Counting Time Zones (Pages 428-431)
- Using `value_counts()` to summarize categorical data
- Handling missing data with `fillna()`
- Replacing empty strings with "Unknown"
- Visualizing with matplotlib bar charts
- Introduction to seaborn for enhanced visualizations

### 13.3 Analyzing by Operating System (Pages 431-434)
- Filtering data subsets
- Creating new columns based on conditions
  - `np.where()` for conditional logic
  - `str.contains()` for pattern matching
- Grouping data with `groupby()`
- Aggregating with `size()` and `unstack()`
- Selecting top time zones
- Comparing Windows vs non-Windows users

### 13.4 (Additional) Linear Models Introduction (Pages 416-419)
- Brief introduction to statsmodels OLS regression
- Formula API with Patsy
- scikit-learn basic concepts
- Titanic dataset example

## Structured Learning Path

### Phase 1: Environment Setup
```python
# Install required libraries
pip install pandas numpy matplotlib seaborn statsmodels scikit-learn

# Import libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
```

### Phase 2: Load and Explore the Data
```python
# Load the Bitly dataset
records = pd.read_csv('datasets/bitly-data/bitly-data.csv')  # or similar path

# Examine structure
print(records.columns)
print(records.shape)
print(records.head())

# Check time zone column
print(records["tz"].head())
```

### Phase 3: Time Zone Analysis (Section 13.2)
```python
# Basic counting
tz_counts = records["tz"].value_counts()
print(tz_counts.head(10))

# Handle missing data
clean_tz = records["tz"].fillna("Missing")
clean_tz[clean_tz == ""] = "Unknown"
clean_tz_counts = clean_tz.value_counts()

# Plot
clean_tz_counts.head(10).plot(kind='bar')
plt.title("Top 10 Time Zones")
plt.xlabel("Time Zone")
plt.ylabel("Count")
plt.show()
```

### Phase 4: Operating System Analysis (Section 13.3)
```python
# Filter to rows with known agent strings
cframe = records[records["a"].notna()].copy()

# Create OS column
cframe["os"] = np.where(cframe["a"].str.contains("Windows"),
                        "Windows", "Not Windows")

# Group by time zone and OS
by_tz_os = cframe.groupby(["tz", "os"])
agg_counts = by_tz_os.size().unstack().fillna(0)

# Select top 10 time zones
indexer = agg_counts.sum("columns").argsort()
count_subset = agg_counts.take(indexer[-10:])

# Plot
count_subset.plot(kind='bar', figsize=(10, 6))
plt.title("Top 10 Time Zones by Operating System")
plt.xlabel("Time Zone")
plt.ylabel("Count")
plt.legend(["Not Windows", "Windows"])
plt.show()
```

### Phase 5: Reproduce Key Visualizations
- Figure 13-1: Horizontal bar plot of top time zones
- Figure 13-2: Grouped bar chart showing Windows vs non-Windows

## Practice Exercises

1. **Explore the dataset**: What other columns exist in the records DataFrame? What do they represent?

2. **Missing data analysis**: What percentage of time zones are missing? What about empty strings?

3. **Custom visualization**: Create a pie chart of the top 5 time zones instead of a bar chart.

4. **Add a third dimension**: Can you break down the analysis by another categorical variable (e.g., browser type)?

5. **Different dataset**: Apply the same analysis pattern to a different dataset you have access to.

## Key Takeaways
- Real-world data analysis workflow: load → clean → analyze → visualize
- pandas `value_counts()`, `fillna()`, `groupby()`, and `unstack()` are powerful tools
- seaborn provides nice enhancements to matplotlib visualizations
- Always handle missing data explicitly
- Grouping and aggregation reveal patterns in categorical data

## Additional Resources
- Chapter 12 (Introduction to Modeling Libraries) for regression concepts
- pandas documentation for `value_counts()`, `groupby()`, and `fillna()`
- seaborn documentation for statistical data visualization