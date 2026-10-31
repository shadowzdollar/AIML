import numpy as np 
import pandas as pd



#string manipulation 

val = "a, b, guido"
print(val.split(","))

#removing the whit spaces

pieces = [x.strip() for x in val.split(",")]


print(pieces)

print("guido" in val)
