import requests
from bs4 import BeautifulSoup
import pandas as pd

# 1. The web pages you want to scrape
urls = [
    "http://npr.org",
    "http://bbc.com",
    "https://edition.cnn.com/world"
]

headers = {
    "User-Agent": "Mozilla/5.0"
}

# This list will hold our clean rows
all_rows = []

for url in urls:
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # 2. Grab ONLY headings (h1, h2, h3) - NOT the whole body!
        headings = soup.find_all(["h1", "h2", "h3"])

        for h in headings:
            text = h.text.strip()

            # Skip empty or very short junk lines
            if len(text) > 10:
                # Add one row at a time
                all_rows.append({
                    "Website": url,
                    "Heading": text
                })

    except Exception as e:
        print(f"Could not load {url}")

# 3. Save directly to Excel using Pandas
df = pd.DataFrame(all_rows)
df.to_excel("my_scraped_data.xlsx", index=False)

print("Done! Check your folder for 'my_scraped_data.xlsx'")