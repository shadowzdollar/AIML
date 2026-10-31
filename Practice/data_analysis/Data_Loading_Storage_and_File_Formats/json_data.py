obj = """
{"name": "Wes",
"cities_lived": ["Akron", "Nashville", "New York", "San Francisco"],
"pet": null,
"siblings": [{"name": "Scott", "age": 34, "hobbies": ["guitars", "soccer"]},
{"name": "Katie", "age": 42, "hobbies": ["diving", "art"]}]
}
"""
import pandas as pd
import sys
import json

result = json.loads(obj)

print(result)

#converting object back to json using dump

asjson = json.dumps(result)

print(asjson)

#converting the json to the dataframe

siblings = pd.DataFrame(result["siblings"], columns=["name", "age"])

print(siblings)

#using panda.read_json

data = pd.read_json("examples/example.json")

print(data)

#exporting data back to json 

data.to_json(sys.stdout)