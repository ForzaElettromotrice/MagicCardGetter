import os
from http.client import responses

import requests
import bs4
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

        params = {"name": f'+{"+".join(f"[{x}]" for x in card.split(" "))}'}
        response = requests.get(BASE_URL, params=params)

        if "en-us" not in response.url:
            print(f"Card not found!")
            continue

        response = requests.get(response.url.replace("en-us", "it-it"))
        soup = BeautifulSoup(response.text, "html.parser")

        img_tag = soup.find_all("img")

        img = img_tag[3]["src"]

        try:
            img = requests.get(img)
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
