import requests
import pandas as pd
from bs4 import BeautifulSoup

import time

urls = [
    "http://igihe.com",
    "http://wikipedia.com",
    "http://apple.com"
]

headers = {
    "User-Agent": "Mozilla/5.0 (compatible; MyScraper/1.0)"
}

#creating the array to store the result scrapped

results = []

with requests.session() as session:
    session.headers.update(headers)


    for url in urls:
        try:

           response = session.get(url, timeout=10)
           response.raise_for_status()
           soup = BeautifulSoup(response.text, "html.parser")
           titles = soup.select("body")


           data = []


           for title in titles:
               contents = title.get_text(strip=True)
               data.append(contents)

           data = {
              "Source": url,
              "Fetched titles": data
                } 

           results.append(data)

        except requests.RequestException() as e:
           print(f"failed to fetch {url}: {e}")

        time.sleep(1)

df = pd.DataFrame(results, index=False)




          
