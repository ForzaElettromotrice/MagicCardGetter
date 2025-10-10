import re
from typing import List, Dict

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://gatherer.wizards.com"
FILE_PATH = "cards.txt"
OUTPUT_DIR = "out_images"

def parse_line(line: str) -> Dict[str, str | int]:
    first, second = line.split("(")
    n, name = first.split(" ", 1)
    code_set, number_set = second.split(")")

    if code_set == "PLST":
        code_set, number_set = number_set.split()[0].split("-")
    else:
        number_set = number_set.split()[0]
    return { "n": int(n), "name": re.sub(r'[^a-z ]+', '', name.strip().lower()), "code_set": code_set, "number_set": int(number_set) }
def read_cards() -> List[Dict[str, str | int]]:
    with open(FILE_PATH) as f:
        cards = [parse_line(line) for line in f]
    return cards

def find_card_url(name: str, code_set: str, number_set: int) -> str:
    return f"{BASE_URL}/{code_set}/it-it/{number_set}/{name.replace(" ", "-")}"
def get_image_url(url: str) -> str:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    imgs = soup.find_all("img")
    for img in imgs:
        if img.has_attr("data-testid") and img["data-testid"] == "cardFrontImage":
            return img.get("src")
    return ""

def save_image(url: str, n: int, name: str):
    response = requests.get(url)
    if n == 1:
        with open(f"{OUTPUT_DIR}/{name}.webp", "wb") as f:
            f.write(response.content)
        return
    for i in range(n):
        with open(f"{OUTPUT_DIR}/{name}_{i}.webp", "wb") as f:
            f.write(response.content)

def main():
    cards = read_cards()

    for diz in cards:
        n, name, code_set, number_set = diz.values()
        url = find_card_url(name, code_set, number_set)
        image_url = get_image_url(url)
        if image_url == "":
            print(f"Card {name} not found")
            continue
        save_image(image_url, n, name)
        print(f"Card {name} saved")

if __name__ == '__main__':
    main()
