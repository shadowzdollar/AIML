import pandas as pd
import os
import numpy as np

frame = pd.DataFrame({"a": np.random.standard_normal(100)})

TEST_DIR =  "/home/luqmaan/Documents/AI(ML)/Practice/Data_Loading_Storage_and_File_Formats/examples"

path = os.path.join(TEST_DIR, "ex1.csv")


store = pd.HDFStore(path)

print(store)

#outputing it as the object instead of csv file

print(store["obj1"])

#providing output into the tabular format

store.put("obj2", frame, format="table")


print(store.select("obj2", where=["index >= 10 and index <=15"]))



