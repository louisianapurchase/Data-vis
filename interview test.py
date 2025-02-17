import requests
from bs4 import BeautifulSoup
import pandas as pd

def fetch_google_doc(url):
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to fetch document")
        return None
    return response.text

def parse_google_doc(html):
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")   
    if not table:
        print("No table found in the document")
        return None
    data = []
    for row in table.find_all("tr")[1:]:  
        cols = row.find_all("td")
        if len(cols) < 3:
            continue
        x = int(cols[0].text.strip())
        char = cols[1].text.strip()
        y = int(cols[2].text.strip())
        data.append((x, y, char))

    return data

def print_grid(data):
    if not data:
        print("No data to display")
        return
    # Determine grid size
    max_x = max(row[0] for row in data)
    max_y = max(row[1] for row in data)
    grid = [[" " for _ in range(max_x + 1)] for _ in range(max_y + 1)]
   # Place characters in grid
    for x, y, char in data:
        grid[max_y - y][x] = char  
    # Print grid
    for row in grid:
        print("".join(row))


url = "https://docs.google.com/document/d/e/2PACX-1vQGUck9HIFCyezsrBSnmENk5ieJuYwpt7YHYEzeNJkIb9OSDdx-ov2nRNReKQyey-cwJOoEKUhLmN9z/pub"
html = fetch_google_doc(url)
data = parse_google_doc(html)

if data:
    print_grid(data)
