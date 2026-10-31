import numpy as np
import pandas as pd

#removing the duplicates

data = pd.DataFrame({"k1": ["one", "two"] * 3 + ["two"],

"k2": [1, 1, 2, 3, 3, 4, 4]})

print(data)

print(data.drop_duplicates())


#specifying the column name to remove the duplicate completely

print(data.drop_duplicates(subset=["k1"]))


#transforming data using function or mapping

data = pd.DataFrame({"food": ["bacon", "pulled pork", "bacon",

"pastrami", "corned beef", "bacon",

"pastrami", "honey ham", "nova lox"],

"ounces": [4, 3, 12, 6, 7.5, 8, 3, 5, 6]})


print(data)

#food and animal source referencing



meat_to_animal = {
"bacon": "pig",
"pulled pork": "pig",
"pastrami": "cow",
"corned beef": "cow",
"honey ham": "pig",
"nova lox": "salmon"
}


#mapping the food from the data object to the meat_to_anima object

data["animal"] = data["food"].map(meat_to_animal)

print(data)

#replacing the values




