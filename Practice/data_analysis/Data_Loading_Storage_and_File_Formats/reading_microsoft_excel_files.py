import pandas as pd
import os 


TEST_DIR =  "/home/luqmaan/Documents/AI(ML)/Practice/Data_Loading_Storage_and_File_Formats/examples"

path = os.path.join(TEST_DIR, "ex1.xlsx")

xlsx = pd.ExcelFile(path)

print(xlsx)

#listing the sheet names

print(xlsx.sheet_names)

#using parse to read the data contained inside the sheet

print(xlsx.parse(sheet_name='Sheet1'))

#using the index column argument

print(xlsx.parse(sheet_name="Sheet1", index_col=0))


#writting pandas data into the excel file

writer = pd.ExcelWriter(path)
frame.to_excel(writer, "Sheet1")

writer.save()

#direct passing the path in the file

frame.to_excel(path, "sheet1")





