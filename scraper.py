import requests
from bs4 import BeautifulSoup

def scrape_quotes(url):
    """Scrapes quotes from a given URL."""
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    quotes = soup.find_all("div", class_="quote")

    for quote in quotes:
        text = quote.find("span", class_="text").text
        author = quote.find("small", class_="author").text
        print(f'"{text}" - {author}')

# Start with the first page
base_url = "http://quotes.toscrape.com/"
url = base_url

while True:
    # Scrape the current page
    scrape_quotes(url)

    # Find the "Next" page link
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    next_page = soup.find("li", class_="next")

    if next_page:
        url = base_url + next_page.find("a")["href"]
    else:
        break  # No more pages
