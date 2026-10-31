#multi pages scraping
import pandas as pd
import requests 
from bs4 import BeautifulSoup

import time

urls = [
    "http://igihe.com",
    "http://apple.com",
    "http://wikipedia.com"
]

headers = {
    "User-Agent": "Mozilla/5.0 (compatible; MyScraper/1.0)"
}

results = []

with requests.session() as session:
    session.headers.update(headers)

    for url in urls:
        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            titles = soup.find_all("h2")

            data = []

            for title in titles:
                contents = title.get_text(strip=True)
                data.append(contents)

            fetched_data = {
                "source": url,
                "data": data
            }

            results.append(fetched_data)

        except requests.RequestException() as e:
            print(f"Unable to fetch {url}: {e}")

    print(results)


    #there are two ways to read the excel file

    #using pd.ExcelFile

    xlsx = pd.ExcelFile(path)

    print(xlsx)

    #the sencond way using the pd.read_excel

    frame = pd.read_excel(path)

    print(frame)

    #adding the column index attribute and outputin only thesheet names

    #printing out the sheet names

    print(xlsx.sheet_names)

    #reading the data contained in a certain sheet


    print(xlsx.parse(sheet_name = "Sheet1"))

    #suggesting the index fol

    print(xlsx.parse(sheet_name = "Sheet1", index_col=0))

    #writing the excel file and converting

    writer = pd.ExcelWriter(path)
    frame.to_excel(writer, "Sheet2")

    #direct use of the path and sheet stating

    frame.read_excel(path, "sheet2")
    

