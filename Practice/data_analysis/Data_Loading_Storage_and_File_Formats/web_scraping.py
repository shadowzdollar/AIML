#single page scraping

import requests

from bs4 import BeautifulSoup


url = "http://igihe.com"

response = requests.get(url)

soup = BeautifulSoup(response.text, "html.parser")

titles = soup.find_all("h2")

for title in titles:
    contents = title.get_text(strip=True)
    print(contents)


    

