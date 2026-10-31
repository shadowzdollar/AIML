import pandas as pd

#reading te html files

tables = pd.read_html("examples/fdisc_failed_bank_list.html")

#calculating the number of the tables found in a certain html file

print(len(tables))

failures = tables[0]


#selecting the first five rws of data
print(failures.head())



#computing the number of bank failures dby year

close_timestamps = pd.to_datetime(failures["Closing Date"])

#counting the number of the failed banks each year based on the close stamps



print(close_timestamps.dt.year.value_counts())

#Parsing XML with lxml.objectify







