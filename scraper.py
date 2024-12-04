import requests
from bs4 import BeautifulSoup
import pymongo


def scrape_quotes(url):
    """Scrapes quotes and their tags from a given URL."""
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    quotes = soup.find_all("div", class_="quote")

    all_quotes = []
    for quote in quotes:
        text = quote.find("span", class_="text").text
        author = quote.find("small", class_="author").text

        # Extract tags
        tags = [tag.text for tag in quote.find_all("a", class_="tag")]

        all_quotes.append({
            "text": text,
            "author": author,
            "tags": tags
        })

    return all_quotes


# MongoDB connection and setup
client = pymongo.MongoClient("127.0.0.1", 27017)  # Connect to MongoDB
db_name = "quotes_db"  # Replace with your desired database name
collection_name = "quotes"  # Replace with your desired collection name

db = client[db_name]  # Get the database
collection = db[collection_name]  # Get the collection

# Start with the first page
base_url = "http://quotes.toscrape.com/"
url = base_url

while True:
    # Scrape the current page
    quotes = scrape_quotes(url)

    # Insert quotes into MongoDB
    if quotes:
        collection.insert_many(quotes)

    # Find the "Next" page link
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    next_page = soup.find("li", class_="next")

    if next_page:
        url = base_url + next_page.find("a")["href"]
    else:
        break  # No more pages

print("Quotes scraped and stored in MongoDB.")

# Close the MongoDB connection
client.close()