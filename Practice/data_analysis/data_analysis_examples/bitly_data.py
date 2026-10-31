path = "/home/ghost/Documents/AI(ML)/Practice/pydata-book/datasets/bitly_usagov/example.txt"

with open(path) as f:
    print(f.readline())


#convertin json into python objects

import json

with open(path) as f:
    records = [json.loads(line) for line in f]
    print(records[1])



#converting it backs to the json format

with open(path) as f:
    json_data = json.dumps(records, indent=4)
    print(json_data)


