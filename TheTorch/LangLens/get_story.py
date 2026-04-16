from bs4 import BeautifulSoup
import os

# The raw text from Citation 1
citation_text = "LangLens/holms.html"

# Parse the HTML string
with open(citation_text , 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')
    all_div = soup.find_all('a')
    for div in all_div:
        print(div)
      # Print the parsed HTML in a readable format
# # Access elements
# print(soup.title.string)
