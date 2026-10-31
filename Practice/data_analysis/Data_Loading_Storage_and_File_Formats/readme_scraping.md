Example: Scraping Multiple Sites into One Dataset

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

headers = {"User-Agent": "Mozilla/5.0"}

def scrape_site_a(url):
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    items = []
    for product in soup.select(".product-card"):
        items.append({
            "source": "SiteA",
            "title": product.select_one(".title").text.strip(),
            "price": product.select_one(".price").text.strip(),
        })
    return items

def scrape_site_b(url):
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    items = []
    for product in soup.select("div.item"):
        items.append({
            "source": "SiteB",
            "title": product.find("h3").text.strip(),
            "price": product.find("span", class_="cost").text.strip(),
        })
    return items

# Combine results from multiple sites
all_data = []
all_data += scrape_site_a("https://sitea.com/products")
time.sleep(1)  # be polite, avoid hammering servers
all_data += scrape_site_b("https://siteb.com/products")

# Save to one unified dataset
df = pd.DataFrame(all_data)
df.to_csv("combined_data.csv", index=False)
print(df.head())



Scaling It Up: Scrapy Framework


import scrapy

class SiteASpider(scrapy.Spider):
    name = "site_a"
    start_urls = ["https://sitea.com/products"]

    def parse(self, response):
        for product in response.css(".product-card"):
            yield {
                "source": "SiteA",
                "title": product.css(".title::text").get(),
                "price": product.css(".price::text").get(),
            }



# example: news/blog scraping

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

headers = {"User-Agent": "Mozilla/5.0"}

def get_article_links(listing_url):
    """Step 1: scrape the listing/homepage for article links"""
    r = requests.get(listing_url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    links = []
    for a in soup.select("h2 a, h3 a"):  # common pattern for headlines
        href = a.get("href")
        if href and href.startswith("http"):
            links.append(href)
    return list(set(links))  # remove duplicates

def scrape_article(url):
    """Step 2: visit each article page and extract details"""
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        title = soup.find("h1")
        title = title.text.strip() if title else None

        author = soup.find(class_="author")
        author = author.text.strip() if author else "Unknown"

        date = soup.find("time")
        date = date.get("datetime") if date else None

        paragraphs = soup.find_all("p")
        body = " ".join(p.text.strip() for p in paragraphs[:5])  # first few paragraphs

        return {
            "url": url,
            "title": title,
            "author": author,
            "date": date,
            "summary": body
        }
    except Exception as e:
        print(f"Failed on {url}: {e}")
        return None

# --- Run it ---
listing_url = "https://example-news-site.com"
article_links = get_article_links(listing_url)

results = []
for link in article_links:
    data = scrape_article(link)
    if data:
        results.append(data)
    time.sleep(1)  # polite delay

df = pd.DataFrame(results)
df.to_csv("news_articles.csv", index=False)
print(df.head())