import pandas as pd
import numpy as np

price = pd.read_pickle("examples/yahoo_price.pkl")
volume = pd.read_pickle("examples/yahoo_volume.pkl")

#obtain the percentage changes 

returns = price.ptc_changes()

#selecting the last five

print(returns.tail())

#determing hte correlation

returns["MSFT"].corr(returns["IBM"])

#also teh covarient

returns["MSFT"].cov(returns["IBM"])

#corr and cov of all returns

returns.corr()
returns.cov()

