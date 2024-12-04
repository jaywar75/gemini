import requests
from bs4 import BeautifulSoup
import pymongo
from pymongo.errors import ConnectionFailure

def scrape_quotes(page_url):
    """
    Scrapes quotes and their tags from a given URL.

    Args:
        page_url (str): The URL of the page to scrape.

    Returns:
        list: A list of dictionaries, each containing a quote, author, and tags.
              Returns an empty list if there's an error.
    """
    try:
        response = requests.get(page_url)
        response.raise_for_status()

        page_soup = BeautifulSoup(response.content, "html.parser")
        page_quotes = page_soup.find_all("div", class_="quote")

        all_quotes = []
        for quote in page_quotes:
            try:
                text = quote.find("span", class_="text").text
                author = quote.find("small", class_="author").text

                # Refactored list comprehension into a for loop
                tags = []
                for tag in quote.find_all("a", class_="tag"):
                    tags.append(tag.text)

                all_quotes.append({
                    "text": text,
                    "author": author,
                    "tags": tags
                })
            except AttributeError as attrib_error:
                print(f"Error extracting quote data: {attrib_error}")
                continue

        return all_quotes

    except requests.exceptions.RequestException as req_error:
        print(f"Error fetching URL {page_url}: {req_error}")
        return []

# MongoDB connection and setup
try:
    client = pymongo.MongoClient("127.0.0.1", 27017, serverSelectionTimeoutMS=5000)
    client.server_info()
    db_name = "quotes_db"
    collection_name = "quotes"
    db = client[db_name]
    collection = db[collection_name]
except ConnectionFailure as conn_error:
    print(f"Error connecting to MongoDB: {conn_error}")
    exit(1)

# Start with the first page
base_url = "https://quotes.toscrape.com/"
url = base_url

while True:
    # Scrape the current page
    quotes = scrape_quotes(url)

    # Insert quotes into MongoDB
    if quotes:
        try:
            collection.insert_many(quotes)
        except pymongo.errors.PyMongoError as mongo_error:
            print(f"Error inserting quotes into MongoDB: {mongo_error}")

    # Find the "Next" page link
    try:
        soup = BeautifulSoup(requests.get(url).content, "html.parser")
        next_page = soup.find("li", class_="next")
    except requests.exceptions.RequestException as req_error:
        print(f"Error fetching URL {url} for pagination: {req_error}")
        break

    if next_page:
        url = base_url + next_page.find("a")["href"]
    else:
        break

print("Quotes scraped and stored in MongoDB (with error handling).")

# Close the MongoDB connection
client.close()