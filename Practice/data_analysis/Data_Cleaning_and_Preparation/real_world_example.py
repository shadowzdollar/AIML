#Real data cleaning and preparation example in the real world

import pandas as pd
import numpy as np
import re

# Raw, messy dataset (simulating a real export)
data = pd.DataFrame({
    'customer_id': [101, 102, 103, 104, 105, 106],
    'email': ['Jane.Doe@Gmail.com ', 'bob123@YAHOO.com', np.nan,
              'sara_k@outlook.com', 'mike.t@gmail.com', 'liz@hotmail.COM'],
    'region': ['west', 'west', np.nan, 'east', 'east', np.nan],
    'order_amount': [250.0, np.nan, 180.0, np.nan, 90.0, 300.0],
    'tier': ['gold', 'silver', 'gold', 'bronze', 'silver', 'gold']
})

print(data)



#1 cleaning the email column with regex

def clean_email(x):
    if pd.isna(x):
        return x
    x =x.strip().lower()
    if re.match(r"[^@]+@[^@]+\.[^@]+", x):
        return x
    return np.nan

data['email'] = data['email'].apply(clean_email)

print(data)

#fill in the missing regions using the forward fill

data['region'] = data['region'].fillna(method='ffill')

#filling the empy spaces in teh ordered amount using forward fill

data['order_amount'] = data['order_amount'].fillna(method='ffill')

#converting tier to category dtype and ensure that they are ordered

data['tier'] = pd.Categorical(data['tier'], categories=['bronze', 'silver', 'gold'], ordered=True)

#for this stage the category comparison can be done

data[data['tier'] > 'bronze']

#creating dummy variables

region_dummies = pd.get_dummies(data['region'], prefix='region')
data = data.join(region_dummies)


sampler = np.random.permutation(len(data))
data_shuffled = data.iloc[sampler].reset_index(drop=True)