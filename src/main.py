import os
import re
from io import BytesIO
from typing import List, Dict, Tuple

import requests
from PIL import Image
from PIL.ImageFile import ImageFile
from bs4 import BeautifulSoup

WIZARDS_GATHERER_BASE_URL = "https://gatherer.wizards.com"
SCRYFALL_BASE_URL = "https://api.scryfall.com"
FILE_PATH = "cards.txt"
OUTPUT_DIR = "out_images"

MIN_WIDTH = 500
MIN_HEIGHT = 800

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

def save_image(img: ImageFile, n: int, name: str):
    name = name.replace(" ", "_")
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    if n == 1:
        img.save(f"{OUTPUT_DIR}/{name}.webp")
        return
    for i in range(n):
        img.save(f"{OUTPUT_DIR}/{name}_{i + 1}.webp")

def check_image(url: str) -> Tuple[bool, ImageFile]:
    response = requests.get(url)

    with Image.open(BytesIO(response.content)) as im:
        if im.width >= MIN_WIDTH and im.height >= MIN_HEIGHT:
            return True, im
        else:
            return False, im

def get_card(name: str, code_set: str, number_set: str, n: int)-> bool:
    versions = get_versions(name)
    versions.sort(key = lambda card: (card[0].lower() == code_set.lower(), card[1] == number_set), reverse = True)

    imgs:list[ImageFile] = []
    for set_, number in versions:
        url = find_card_url(name, set_, number)
        image_url = get_image_url(url)
        if image_url == "":
            continue
        ok, img = check_image(image_url)
        imgs.append(img)
        if not ok:
            continue
        save_image(img, n, name)
        return True

    if len(imgs) == 0:
        return False

    imgs.sort(key = lambda im: im.width * im.height, reverse = True)
    img = imgs[0]
    save_image(img, n, name)

    return True

def main():
    cards = read_cards()

    for diz in cards:
        n, name, code_set, number_set = diz.values()
        if get_card(name, code_set, number_set, n):
            print(f"Card {name} downloaded")
        else:
            print(f"Card {name} not found")

if __name__ == '__main__':
    main()
