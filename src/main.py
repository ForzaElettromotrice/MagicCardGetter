import os
import re
import tomllib
from io import BytesIO
from typing import List, Dict, Tuple

import requests
from PIL import Image
from PIL.ImageFile import ImageFile
from bs4 import BeautifulSoup

WIZARDS_GATHERER_BASE_URL = "https://gatherer.wizards.com"
SCRYFALL_BASE_URL = "https://api.scryfall.com"
def deep_update(a: dict, b: dict) -> dict:
    for k, v in b.items():
        if k in a and isinstance(a[k], dict) and isinstance(v, dict):
            deep_update(a[k], v)
        else:
            a[k] = v
    return a
def load_config(path: str = "config.toml") -> dict:
    defaults = {
        "paths": { "file_path": "cards.txt", "output_dir": "out_images" },
        "images": { "min_width": 500, "min_height": 800 },
        "blacklist": { "set": [] }
    }
    if not os.path.exists(path):
        return defaults
    with open(path, "rb") as f:
        data = tomllib.load(f)

    deep_update(defaults, data)

    return defaults

CONFIG = load_config()

FILE_PATH = CONFIG["paths"]["file_path"]
OUTPUT_DIR = CONFIG["paths"]["output_dir"]

MIN_WIDTH = CONFIG["images"]["min_width"]
MIN_HEIGHT = CONFIG["images"]["min_height"]

SET_BLACKLIST = [set_.lower() for set_ in CONFIG["blacklist"]["set"]]

def parse_line(line: str) -> Dict[str, str | int]:
    first, second = line.split("(")
    n, name = first.split(" ", 1)
    if "/" in name:
        name, _ = name.split("/", 1)
    set_code, set_number = second.split(")")

    if set_code == "PLST":
        set_code, set_number = set_number.split()[0].split("-")
    else:
        set_number = set_number.split()[0]
    return { "n": int(n), "name": re.sub(r'[^a-z A-Z-]+', '', name.strip()), "set_code": set_code, "set_number": set_number }
def read_cards() -> List[Dict[str, str | int]]:
    with open(FILE_PATH) as f:
        cards = [parse_line(line) for line in f]
    return cards

def find_card_url(name: str, set_code: str, set_number: str) -> str:
    return f"{WIZARDS_GATHERER_BASE_URL}/{set_code.upper()}/it-it/{set_number}/{name.replace(' ', '-').lower()}"
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
    return [(card["set"], card["collector_number"]) for card in cards if card["set"].lower() not in SET_BLACKLIST]

def get_image(url: str) -> ImageFile:
    response = requests.get(url)
    return Image.open(BytesIO(response.content))
def save_image(img: ImageFile, n: int, name: str):
    name = name.replace(" ", "_")
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    if n == 1:
        img.save(f"{OUTPUT_DIR}/{name}.webp")
        return
    for i in range(n):
        img.save(f"{OUTPUT_DIR}/{name}_{i + 1}.webp")

def process_card(name: str, set_code: str, set_number: str):
    url = find_card_url(name, set_code, set_number)
    image_url = get_image_url(url)
    if image_url == "":
        return None
    img = get_image(image_url)
    return img

def get_card(name: str, set_code: str, set_number: str, n: int) -> bool:
    versions = get_versions(name)
    versions.sort(key = lambda card: (card[0].lower() == set_code.lower(), card[1] == set_number), reverse = True)

    imgs: list[ImageFile] = [process_card(name, set_, number) for set_, number in versions]
    imgs = [img for img in imgs if img is not None]

    if len(imgs) == 0:
        return False

    if imgs[0].width < MIN_WIDTH or imgs[0].height < MIN_HEIGHT:
        imgs.sort(key = lambda im: im.width * im.height, reverse = True)

    img = imgs[0]
    save_image(img, n, name)
    return True

def main():
    cards = read_cards()

    for diz in cards:
        n, name, set_code, set_number = diz.values()
        if get_card(name, set_code, set_number, n):
            print(f"Card {name} downloaded")
        else:
            print(f"Card {name} not found")

if __name__ == '__main__':
    main()
