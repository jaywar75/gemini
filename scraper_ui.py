import tkinter as tk
from tkinter import ttk, messagebox
import requests
from bs4 import BeautifulSoup
import pymongo
from pymongo.errors import ConnectionFailure
from urllib.parse import urljoin, urlparse
import time
import threading
import logging
from typing import Tuple, List, Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(message)s')

def scrape_quotes(page_url: str) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """
    Scrapes quotes and their tags from a given URL.
    """
    try:
        response = requests.get(page_url)
        response.raise_for_status()

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

        next_page = page_soup.find("li", class_="next")
        if next_page:
            next_page_link = next_page.find("a")["href"]
            next_page_url = urljoin(page_url, next_page_link)
        else:
            next_page_url = None

        return all_quotes, next_page_url

    except requests.exceptions.RequestException as req_error:
        logging.error(f"Error fetching URL {page_url}: {req_error}")
        return [], None

def connect_to_mongodb(db_name: str, collection_name: str, host: str, port: int):
    try:
        client = pymongo.MongoClient(host, port, serverSelectionTimeoutMS=5000)
        client.server_info()
        db = client[db_name]
        collection = db[collection_name]
        return client, collection
    except ConnectionFailure as e:
        logging.error(f"Error connecting to MongoDB: {e}")
        messagebox.showerror("Error", f"Error connecting to MongoDB: {e}")
        return None, None

def main():
    def scrape_data():
        status_label.config(text="Status: Scraping in progress...")
        try:
            url = url_entry.get().strip()
            delay = float(delay_entry.get())
            db_name = db_name_entry.get().strip()
            collection_name = collection_name_entry.get().strip()
            host = host_entry.get().strip()
            port = int(port_entry.get().strip())

            if not urlparse(url).scheme:
                messagebox.showerror("Error", "Please enter a valid URL.")
                status_label.config(text="Status: Ready")
                return

            if delay < 2:
                messagebox.showerror("Error", "Loop delay must be at least 2 seconds.")
                status_label.config(text="Status: Ready")
                return

            client, collection = connect_to_mongodb(db_name, collection_name, host, port)
            if not client:
                status_label.config(text="Status: Ready")
                return

            # Create unique index to prevent duplicates
            collection.create_index(
                [('text', pymongo.ASCENDING), ('author', pymongo.ASCENDING)],
                unique=True
            )

            while url:
                quotes, next_page_url = scrape_quotes(url)
                if quotes:
                    for quote in quotes:
                        try:
                            collection.update_one(
                                {'text': quote['text'], 'author': quote['author']},
                                {'$setOnInsert': quote},
                                upsert=True
                            )
                        except pymongo.errors.DuplicateKeyError:
                            logging.info("Duplicate quote found and skipped.")
                else:
                    logging.info("No quotes found on the page.")
                    break
                time.sleep(delay)
                url = next_page_url

            messagebox.showinfo("Success", "Quotes scraped and stored in MongoDB.")
            status_label.config(text="Status: Scraping completed successfully.")
        except ValueError as ve:
            messagebox.showerror("Error", f"Invalid input: {ve}")
            status_label.config(text="Status: Ready")
        except Exception as e:
            logging.exception("An unexpected error occurred.")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
            status_label.config(text="Status: Ready")
        finally:
            if 'client' in locals():
                client.close()

    # Create main window
    root = tk.Tk()
    root.title("Web Scraper")

    # Input frame
    input_frame = ttk.Frame(root, padding="10")
    input_frame.grid(row=0, column=0, padx=10, pady=10)

    # Website URL
    url_label = ttk.Label(input_frame, text="Website URL:")
    url_label.grid(row=0, column=0, sticky=tk.W, pady=5)
    url_entry = ttk.Entry(input_frame, width=50)
    url_entry.grid(row=0, column=1, pady=5)

    # Loop delay
    delay_label = ttk.Label(input_frame, text="Loop delay (seconds):")
    delay_label.grid(row=1, column=0, sticky=tk.W, pady=5)
    delay_entry = ttk.Entry(input_frame, width=10)
    delay_entry.grid(row=1, column=1, pady=5)
    delay_entry.insert(0, "2")

    # Database name
    db_name_label = ttk.Label(input_frame, text="Database name:")
    db_name_label.grid(row=2, column=0, sticky=tk.W, pady=5)
    db_name_entry = ttk.Entry(input_frame, width=30)
    db_name_entry.grid(row=2, column=1, pady=5)
    db_name_entry.insert(0, "quotes_db")

    # Collection name
    collection_name_label = ttk.Label(input_frame, text="Collection name:")
    collection_name_label.grid(row=3, column=0, sticky=tk.W, pady=5)
    collection_name_entry = ttk.Entry(input_frame, width=30)
    collection_name_entry.grid(row=3, column=1, pady=5)
    collection_name_entry.insert(0, "quotes")

    # MongoDB Host
    host_label = ttk.Label(input_frame, text="MongoDB Host:")
    host_label.grid(row=4, column=0, sticky=tk.W, pady=5)
    host_entry = ttk.Entry(input_frame, width=30)
    host_entry.grid(row=4, column=1, pady=5)
    host_entry.insert(0, "127.0.0.1")

    # MongoDB Port
    port_label = ttk.Label(input_frame, text="MongoDB Port:")
    port_label.grid(row=5, column=0, sticky=tk.W, pady=5)
    port_entry = ttk.Entry(input_frame, width=10)
    port_entry.grid(row=5, column=1, pady=5)
    port_entry.insert(0, "27017")

    # Scrape button
    scrape_button = ttk.Button(root, text="Scrape", command=lambda: threading.Thread(target=scrape_data).start())
    scrape_button.grid(row=1, column=0, pady=10)

    # Status label
    status_label = ttk.Label(root, text="Status: Ready")
    status_label.grid(row=2, column=0, pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()