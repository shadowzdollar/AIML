import pandas as pd
import os

TEST_DIR = "/home/luqmaan/Documents/AI(ML)/Practice/Data_Loading_Storage_and_File_Formats/examples"


frame = pd.read_csv(os.path.join(TEST_DIR, "ex1.csv"))

print(frame)


#using pickle to store or serialize the binary data

frame.to_pickle("frame_pickle")

pickle_output = pd.read_pickle("frame_pickle")


print(pickle_output)

#usinf parque from pyarrow

fec = pd.read_parquet('datasets/fec/fec.parquet')


