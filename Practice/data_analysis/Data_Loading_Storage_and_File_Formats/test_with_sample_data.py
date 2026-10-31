import pandas as pd
from lxml import objectify

path = "/home/luqmaan/Documents/AI(ML)/Practice/Data_Loading_Storage_and_File_Formats/Performance_MNR.xml"

with open(path) as f:
    parsed = objectify.parse(f)

root = parsed.getroot()


data = []

#skiping specific elements

skip_fields = ["PARENT_SEQ", "INDICATOR_SEQ",
"DESIRED_CHANGE", "DECIMAL_PLACES"]

for el in root.INDICATOR:
    el_data = {}
    for child in el.getchildren():
        if child.tag in skip_fields:
            continue
        el_data[child.tag] = child.pyval
    data.append(el_data)

# converting cthe plain data into the dataframe

perf = pd.DataFrame = (data)


print(perf)

