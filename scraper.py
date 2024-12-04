import requests
from bs4 import BeautifulSoup
import pymongo
from pymongo.errors import ConnectionFailure
from urllib.parse import urljoin
from typing import Tuple, List, Dict, Any, Optional

def scrape_quotes(page_url: str) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """
    Scrapes quotes and their tags from a given URL.

    Args:
        page_url (str): The URL of the page to scrape.

    Returns:
        tuple: A tuple containing:
            - list: A list of dictionaries, each containing a quote, author, and tags.
            - str or None: The URL of the next page, or None if there's no next page.
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

                # Using list comprehension for tags
                tags = [tag.text for tag in quote.find_all("a", class_="tag")]

                all_quotes.append({
                    "text": text,
                    "author": author,
                    "tags": tags
                })
            except AttributeError as attrib_error:
                print(f"Error extracting quote data: {attrib_error}")
                continue

        # Find the "Next" page link using the existing soup
        next_page = page_soup.find("li", class_="next")
        if next_page:
            next_page_link = next_page.find("a")["href"]
            next_page_url = urljoin(page_url, next_page_link)
        else:
            next_page_url = None

        return all_quotes, next_page_url

    except requests.exceptions.RequestException as req_error:
        print(f"Error fetching URL {page_url}: {req_error}")
        return [], None

def main():
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

    while url:
        # Scrape the current page
        quotes, next_page_url = scrape_quotes(url)

        # Insert quotes into MongoDB
        if quotes:
            try:
                collection.insert_many(quotes)
            except pymongo.errors.PyMongoError as mongo_error:
                print(f"Error inserting quotes into MongoDB: {mongo_error}")

        url = next_page_url

    print("Quotes scraped and stored in MongoDB (with error handling).")

    # Close the MongoDB connection
    client.close()

if __name__ == "__main__":
    main()