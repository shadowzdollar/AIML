import pandas as pd
import numpy as np

obj = pd.Series([4.5, 7.2, -5.3, 3.6], index=["d", "b", "a", "c"])

print(obj)

#reindixing th eobject

obj2 = obj.reindex(["a", "b", "c", "d", "e"])

print(obj2)

#auto filling th eobjects

obj3 = pd.Series(["blue", "purple", "yellow"], index=[0, 2, 4])

obj3.reindex(np.arange(6), method="ffill")

print(obj3)

frame = pd.DataFrame(np.arange(9).reshape((3, 3)), index=["a", "c", "d"], columns=["Ohio", "Texas", "California"])

print(frame)

#tring to reindex

frame2 = frame.reindex(index=["a", "b", "c", "d"])

print(frame2)

#with column keyword

states = ["Texas", "Utah", "California"]

frame.reindex(columns=states)
