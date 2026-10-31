path = "/home/ghost/Documents/AI(ML)/Practice/pydata-book/datasets/bitly_usagov/example.txt"

import json

with open(path) as f:
    records = [json.loads(line) for line in f]


#counting timezones in pure python

time_zones = [rec["tz"] for rec in records]
print(time_zones);




#with the tz missing haldlance

time_zones = [
    rec["tz"]
    for rec in records
    if "tz" in rec
]

print(time_zones)

#counting the occurance

from collections import defaultdict #for assigning the default value

def get_counts(sequence):
    counts = defaultdict(int)
    for x in sequence:
        counts[x] += 1
    return counts


#invoking the function

counts = get_counts(time_zones)

print(counts)




#using pandas

import pandas as pd
frame = pd.DataFrame(records)


tz_counts = frame["tz"].value_counts()

print(tz_counts[:10])

# handling the missing data

tz_counts = frame["tz"].fillna("Missing").value_counts()