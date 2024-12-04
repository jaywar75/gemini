from bs4 import BeautifulSoup

html = """
<div class="quote">
  <span class="text">“The world as we have created it is a process of our thinking.”</span>
  <div class="tags">
    <a class="tag" href="/tag/change/page/1/">change</a>
    <a class="tag" href="/tag/deep-thoughts/page/1/">deep-thoughts</a>
  </div>
</div>
"""

soup = BeautifulSoup(html, "html.parser")
quote = soup.find("div", class_="quote")

print(quote)  # Output the quote object to verify

tags = [tag.text for tag in quote.find_all("a", class_="tag")]
print(tags)