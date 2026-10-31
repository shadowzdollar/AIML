"""
Chapter 13: Data Analysis Examples - Getting Started
Python for Data Analysis by Wes McKinney

This script demonstrates the beginning of Chapter 13, focusing on:
1. Setting up the environment
2. Loading and exploring data
3. Basic time zone analysis

Note: The actual Bitly dataset from the book may need to be downloaded separately.
This script uses sample data to demonstrate the concepts.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set up plotting style
sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (10, 6)

print("=" * 60)
print("CHAPTER 13: DATA ANALYSIS EXAMPLES")
print("=" * 60)
print()
print("Book: Python for Data Analysis by Wes McKinney")
print("Chapter: 13 - Data Analysis Examples (Pages 426-472)")
print()
print("Topic: Analyzing Bitly data from 1.usa.gov")
print()

# ============================================================
# STEP 1: Install required libraries (if not already installed)
# ============================================================
print("STEP 1: Required Libraries")
print("-" * 40)
print("Install with: pip install pandas numpy matplotlib seaborn")
print()
print("Importing libraries...")

# Verify imports work
try:
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    print("✓ All libraries imported successfully!")
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Please install required libraries first.")
    exit(1)

print()

# ============================================================
# STEP 2: Load and explore the dataset
# ============================================================
print("STEP 2: Loading and Exploring Data")
print("-" * 40)
print()
print("The book uses Bitly data from 1.usa.gov")
print("This dataset contains URL shortening logs with browser/OS info")
print()

# Since the actual dataset isn't included, let's create sample data
# that mimics the structure of the Bitly dataset
print("Creating sample data similar to the Bitly dataset...")
print()

# Simulate the records DataFrame structure from the book
np.random.seed(42)  # For reproducibility
n_rows = 1000

# Create sample data
sample_data = {
    'a': np.random.choice(
        ['Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 
         'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
         'GoogleMaps/RochesterNY',
         'Mozilla/5.0 (Linux; U; Android 2.2.2; en-us; LG-P9)'],
        size=n_rows
    ),
    'tz': np.random.choice(
        ['America/New_York', 'America/Denver', 'Europe/London', 
         'Asia/Tokyo', ''],
        size=n_rows,
        p=[0.3, 0.15, 0.15, 0.1, 0.3]
    ),
    'c': np.random.choice(['indeed', 'facebook', 'twitter', 'direct'], size=n_rows),
}

records = pd.DataFrame(sample_data)

print(f"✓ Created DataFrame with {records.shape[0]} rows and {records.shape[1]} columns")
print(f"✓ Column names: {list(records.columns)}")
print()

# ============================================================
# STEP 3: Basic exploration (Section 13.1 concepts)
# ============================================================
print("STEP 3: Basic Exploration (Section 13.1)")
print("-" * 40)
print("Examining the first few rows of data...")
print()

print("First 5 rows of the DataFrame:")
print("=" * 60)
print(records.head())
print()

print("Columns and their types:")
print("=" * 60)
print(records.dtypes)
print()

print("Shape of the data:")
print("=" * 60)
print(f"Rows: {records.shape[0]}")
print(f"Columns: {records.shape[1]}")
print()

# ============================================================
# STEP 4: Time Zone Analysis (Section 13.2 - starting point)
# ============================================================
print("STEP 4: Time Zone Analysis (Intro to Section 13.2)")
print("-" * 40)
print()
print("The book examines time zone distribution in the data...")
print()

# Basic counting of time zones
print("4.1 Basic time zone counts:")
print("=" * 60)
tz_counts = records["tz"].value_counts()
print(tz_counts)
print()

# Handle missing data - concept from the book
print("4.2 Handling missing data:")
print("=" * 60)
print("Note: In the book, they handle missing values with fillna().")
print()

clean_tz = records["tz"].fillna("Missing")
clean_tz[clean_tz == ""] = "Unknown"
clean_tz_counts = clean_tz.value_counts()

print("Cleaned time zone counts (filled NaN as 'Missing', empty as 'Unknown'):")
print("=" * 60)
print(clean_tz_counts.head(10))
print()

# ============================================================
# STEP 5: Basic Visualization
# ============================================================
print("STEP 5: Basic Visualization")
print("-" * 40)
print()
print("Creating a bar plot of top time zones...")
print()

# Plot the top 10 time zones
top_10 = clean_tz_counts.head(10)
top_10.plot(kind='bar', color='steelblue')
plt.title("Top 10 Time Zones (Sample Data)")
plt.xlabel("Time Zone")
plt.ylabel("Count")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()
print("✓ Bar chart displayed above!")
print()

# ============================================================
# STEP 6: Key Concepts Summary
# ============================================================
print("STEP 6: Key Concepts Learned So Far")
print("-" * 40)
print()
print("✓ Loaded data into a pandas DataFrame")
print("✓ Used value_counts() to summarize categorical data")
print("✓ Handled missing data with fillna()")
print("✓ Replaced empty strings with 'Unknown'")
print("✓ Created bar visualizations with matplotlib/seaborn")
print()
print("=" * 60)
print("NEXT STEPS: We'll explore Operating System analysis")
print("          (Section 13.3) and groupby operations")
print("=" * 60)
print()
print("To use the actual Bitly dataset from the book:")
print("- Download from: oreilly.com or GitHub repository")
print("- Place in datasets/ directory as bitly-data.csv")
print("- Update the file path in the code below")
print()

# ============================================================
# EXERCISE: Try it with real data (when available)
# ============================================================
print("EXERCISE:")
print("-" * 40)
print("1. If you have the Bitly dataset, load it with:")
print("   records = pd.read_csv('path/to/bitly-data.csv')")
print()
print("2. Reproduce the time zone analysis:")
print("   tz_counts = records['tz'].value_counts()")
print()
print("3. Handle missing data:")
print("   clean_tz = records['tz'].fillna('Missing')")
print("   clean_tz[clean_tz == ''] = 'Unknown'")
print()
print("4. Create your own visualization:")
print("   clean_tz.head(10).plot(kind='bar')")
print()