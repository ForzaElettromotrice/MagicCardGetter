import os

import requests
from bs4 import BeautifulSoup
from requests.exceptions import MissingSchema

BASE_URL = "https://gatherer.wizards.com"
FILE_PATH = "cards.txt"
OUTPUT_DIR = "out_images"

def main():
    with open(FILE_PATH, "r") as f:
        cards = f.readlines()

    cards = [x.split("(")[0][2:] for x in cards]

    for card in cards:
        print(f"Downloading {card}...", end = "")

        params = { "searchTerm": f'{card.replace(" ", "_")}' }
        response = requests.get(BASE_URL + "/search", params = params)

        soup = BeautifulSoup(response.text, "html.parser")
        divs = soup.find_all("div")

        url = ""

        for div in divs:
            if div.has_attr("data-testid") and div["data-testid"] == "imageListCard":
                url = div.find("a").get("href")
                break
        if url == "":
            print("Not found!")
            continue

        if "en-us" not in url:
            print(f"Card (it-it) not found!")
            continue

        url = url.replace("en-us", "it-it")

        print(f"(it-it)", end = "")
        response = requests.get(BASE_URL + url)
        soup = BeautifulSoup(response.text, "html.parser")

        imgs = soup.find_all("img")
        url = ""
        for img in imgs:
            if img.has_attr("data-testid") and img["data-testid"] == "cardFrontImage":
                url = img.get("src")
                break

        if not url:
            print("Card (it-it) not found!")
            continue

        try:
            img = requests.get(url)
        except MissingSchema:
            print(f"Image not found!")
            continue

        if not os.path.exists(f"{OUTPUT_DIR}"):
            os.makedirs(f"{OUTPUT_DIR}")
        with open(f"{OUTPUT_DIR}/{card}.png", "wb") as f:
            f.write(img.content)
        print(" Done!")

if __name__ == '__main__':
    main()
