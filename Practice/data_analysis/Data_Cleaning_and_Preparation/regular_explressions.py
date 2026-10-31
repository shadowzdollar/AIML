import re 
import numpy as np
import pandas as pd

text = "foo bar\t baz  \tqux"


regex = re.compile(r"\s+")

print(regex.split(text))


#string functions in pandas

data = {"Dave": "dave@google.com", "Steve": "steve@gmail.com", "Rob": "rob@gmail.com", "Wes": np.nan}


print(data)

pdData = pd.Series(data)

print(pdData)

print(pdData.str.contains("gmail"))



