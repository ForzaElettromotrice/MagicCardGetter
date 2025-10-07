import os

import requests
from bs4 import BeautifulSoup
from requests.exceptions import MissingSchema

BASE_URL = "https://gatherer.wizards.com/Pages/Search/Default.aspx"
FILE_PATH = "cards.txt"
OUTPUT_DIR = "out_images"

def main():
    with open(FILE_PATH, "r") as f:
        cards = f.readlines()

    cards = [x.split("(")[0][2:] for x in cards]

    for card in cards:
        print(f"Downloading {card}...", end = "")

        params = { "name": f'+{"+".join(f"[{x}]" for x in card.split(" "))}' }
        response = requests.get(BASE_URL, params = params)

        if "en-us" not in response.url:
            print(f"Card not found!")
            continue

        text = response.text
        url_it = response.url.replace("en-us", "it-it")

        try:
            response = requests.get(url_it)
            text = response.text
        except MissingSchema:
            print(f"(en-us) ", end = "")
            pass
        print(f"(it-it) ", end = "")
        soup = BeautifulSoup(text, "html.parser")

        imgs = soup.find_all("img")
        url = ""
        for img in imgs:
            if img.has_attr("data-testid") and img["data-testid"] == "cardFrontImage":
                url = img.get("src")
                break

        if not url:
            print("QUESTO NON DOVREBBE ESSERE POSSIBILE!")
            continue

        try:
            img = requests.get(url)
        except MissingSchema:
            print(f"Image not found! (my bad)")
            continue

        if not os.path.exists(f"{OUTPUT_DIR}"):
            os.makedirs(f"{OUTPUT_DIR}")
        with open(f"{OUTPUT_DIR}/{card}.png", "wb") as f:
            f.write(img.content)
        print(" Done!")

if __name__ == '__main__':
    main()
