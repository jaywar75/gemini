import requests
from bs4 import BeautifulSoup


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
        tags = [tag.text for tag in quote.find_all("a", class_="tag")]  # List comprehension for conciseness

        all_quotes.append({
            "text": text,
            "author": author,
            "tags": tags
        })

    return all_quotes


# Start with the first page
base_url = "http://quotes.toscrape.com/"
url = base_url
all_quotes = []

while True:
    # Scrape the current page
    all_quotes.extend(scrape_quotes(url))  # Extend the list with new quotes

    # Find the "Next" page link
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    next_page = soup.find("li", class_="next")

    if next_page:
        url = base_url + next_page.find("a")["href"]
    else:
        break  # No more pages

# Print the extracted quotes and tags
for quote in all_quotes:
    print(f'"{quote["text"]}" - {quote["author"]}')
    print("Tags:", ", ".join(quote["tags"]))
    print("---")