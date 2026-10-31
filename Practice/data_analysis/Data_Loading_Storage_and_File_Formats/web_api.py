import requests
import pandas as pd

url = "https://api.github.com/repos/pandas-dev/pandas/issues"

resp = requests.get(url)

#raising for status

resp.raise_for_status()

print(resp)



data = resp.json()

print(data[0]["title"])

issues = pd.DataFrame(data, columns=["number", "title", "labels", "state"])

print(issues[:5])

