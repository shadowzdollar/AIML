# reading the records from teh bitly example


path = "/home/ghost/Documents/AI(ML)/Practice/pydata-book/datasets/bitly_usagov/example.txt"



with open(path) as f:
    print(f.readline())



#converting the data provided into the json format

#first importing the required json package
import json

with open(path) as f:
    records = [json.loads(line) for line in f]


    