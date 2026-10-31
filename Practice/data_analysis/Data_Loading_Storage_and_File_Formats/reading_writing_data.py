import pandas as pd

df = pd.read_csv("examples/ex1.csv")

print(df)

#skippin the header

pd.read_csv("examples/ex1.csv", header=None)

#providiing your own column names

pd.read_csv("examples/ex1.csv", names=["a", "b", "c", "d", "email"])


#naming the index column 


names = ["a", "b", "c", "d", "email"]

pd.read_csv("examples/ex2.csv", names=names, index_col="message")


#hierarchical indexing

parse = pd.read_csv("examples/csv_mindex.csv", index_col=["key1", "key2"])


print(parse)

#separating the whitespaces from the index using the \s+

result = pd.read_csv("examples/ex3.csv", sep="\s+")

print(result)


#skippin rows

pd.read_csv("examples/ex4.csv", skiprows=[0, 2, 3])

#handling the missing na values

#keeping the default na values

pd.read_csv("examples/ex4.csv", keep_default_na=False)

#checking the na values

result.isna()

#nto na

result.notna()


result3 =  pd.read_csv("examples/ex5.csv", keep_default_na=False, na_values=["NA"])

#sentinels specificatio

sentinels = {"message": ["foo", "NA"], "something": ["two"]}

pd.read_csv("examples/ex5.csv", na_values=sentinels, keep_default_na=False)

