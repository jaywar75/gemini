import requests
from bs4 import BeautifulSoup
import pymongo
from pymongo.errors import ConnectionFailure, PyMongoError, DuplicateKeyError
from urllib.parse import urljoin
from typing import Tuple, List, Dict, Any, Optional
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),               # Logs to console
        logging.FileHandler("scraper.log", mode="a")  # Logs to file
    ]
)

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
        response = requests.get(page_url, timeout=10)  # Added timeout
        response.raise_for_status()  # Raise HTTPError for bad responses

        page_soup = BeautifulSoup(response.content, "html.parser")
        page_quotes = page_soup.find_all("div", class_="quote")

        all_quotes = []
        for quote in page_quotes:
            try:
                text = quote.find("span", class_="text").get_text(strip=True)
                author = quote.find("small", class_="author").get_text(strip=True)
                tags = [tag.get_text(strip=True) for tag in quote.find_all("a", class_="tag")]

                all_quotes.append({
                    "text": text,
                    "author": author,
                    "tags": tags
                })
            except AttributeError as attrib_error:
                logging.error(f"Error extracting quote data: {attrib_error}")
                continue

        # Find the "Next" page link
        next_page = page_soup.find("li", class_="next")
        if next_page:
            next_page_link = next_page.find("a")["href"]
            next_page_url = urljoin(page_url, next_page_link)
        else:
            next_page_url = None

        return all_quotes, next_page_url

    except requests.exceptions.HTTPError as http_error:
        logging.error(f"HTTP error fetching URL {page_url}: {http_error}")
        return [], None
    except requests.exceptions.RequestException as req_error:
        logging.error(f"Error fetching URL {page_url}: {req_error}")
        return [], None

def main():
    client = None  # Initialize client to None for safe closure in finally
    try:
        # MongoDB connection and setup
        client = pymongo.MongoClient("127.0.0.1", 27017, serverSelectionTimeoutMS=5000)
        client.server_info()  # Trigger exception if cannot connect
        db_name = "quotes_db"
        collection_name = "quotes"
        db = client[db_name]
        collection = db[collection_name]
        logging.info("Successfully connected to MongoDB.")

        # Create unique index to prevent duplicates
        collection.create_index(
            [('text', pymongo.ASCENDING), ('author', pymongo.ASCENDING)],
            unique=True
        )

        # Start with the first page
        base_url = "https://quotes.toscrape.com/"
        url = base_url

        while url:
            # Scrape the current page
            quotes, next_page_url = scrape_quotes(url)

            if quotes:
                for quote in quotes:
                    try:
                        collection.update_one(
                            {'text': quote['text'], 'author': quote['author']},
                            {'$setOnInsert': quote},
                            upsert=True
                        )
                    except DuplicateKeyError:
                        logging.info("Duplicate quote found and skipped.")
                    except PyMongoError as mongo_error:
                        logging.error(f"Error inserting quote into MongoDB: {mongo_error}")
                logging.info(f"Processed {len(quotes)} quotes from {url}.")
            else:
                logging.info(f"No quotes found on the page: {url}.")
                break  # Exit the loop if no quotes are found

            # Delay to avoid overburdening the server
            time.sleep(5)  # Adjust the delay as needed

            url = next_page_url

        logging.info("Quotes scraped and stored in MongoDB.")

    except ConnectionFailure as conn_error:
        logging.critical(f"Error connecting to MongoDB: {conn_error}")
    except Exception as e:
        logging.exception(f"An unexpected error occurred: {e}")
    finally:
        # Close the MongoDB connection safely
        if client:
            client.close()
            logging.info("MongoDB connection closed.")

if __name__ == "__main__":
    main()