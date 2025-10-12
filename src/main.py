import os
import re
from typing import List, Dict, Tuple

import requests
from bs4 import BeautifulSoup

WIZARDS_GATHERER_BASE_URL = "https://gatherer.wizards.com"
SCRYFALL_BASE_URL = "https://api.scryfall.com"
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
    return { "n": int(n), "name": re.sub(r'[^a-z A-Z]+', '', name.strip()), "code_set": code_set, "number_set": number_set }
def read_cards() -> List[Dict[str, str | int]]:
    with open(FILE_PATH) as f:
        cards = [parse_line(line) for line in f]
    return cards

def find_card_url(name: str, code_set: str, number_set: str) -> str:
    return f"{WIZARDS_GATHERER_BASE_URL}/{code_set.upper()}/it-it/{number_set}/{name.replace(" ", "-").lower()}"
def get_image_url(url: str) -> str:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    imgs = soup.find_all("img")
    for img in imgs:
        if img.has_attr("data-testid") and img["data-testid"] == "cardFrontImage":
            return img.get("src")

    return ""
def get_versions(name: str) -> List[Tuple[str, str]]:
    params = { "exact": name }
    response = requests.get(f"{SCRYFALL_BASE_URL}/cards/named", params = params)
    if "prints_search_uri" not in response.json():
        return []
    response = requests.get(response.json()["prints_search_uri"])

    cards = response.json()["data"]
    return [(card["set"], card["collector_number"]) for card in cards]
def get_another_image_url(name: str) -> str:
    versions = get_versions(name)
    for set_, number in versions:
        url = find_card_url(name, set_, number)
        image_url = get_image_url(url)
        if image_url != "":
            return image_url
    return ""

def save_image(url: str, n: int, name: str):
    response = requests.get(url)

    name = name.replace(" ", "_")
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

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
            image_url = get_another_image_url(name)
            if image_url == "":
                print(f"Card {name} not found")
                continue
        save_image(image_url, n, name)
        print(f"Card {name} saved")

if __name__ == '__main__':
    main()
