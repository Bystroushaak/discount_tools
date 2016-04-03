#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Interpreter version: python 3
#
"""
Tento script stojí na mé zkušenosti s 5% slevovým kódem na alzu FRYDEK5. Z toho
jsem vyvodil hypotézu, že by mohlo existovat více slevových kódů nazvaných
podle měst v čechách.
"""
#
# Imports =====================================================================
import json
import os.path
import unicodedata

from tqdm import tqdm
import requests
if hasattr(requests, "packages"):
    requests.packages.urllib3.disable_warnings()


# Variables ===================================================================
VALID_FN = "valid_codes.txt"
INVALID_FN = "invalid_codes.txt"


# Functions & classes =========================================================
def read_cities():
    with open("mesta.txt") as f:
        return [x for x in f.read().splitlines() if x]


def normalize(line):
    line = line.upper()
    line = unicodedata.normalize('NFKD', line)

    return "".join(c for c in line if not unicodedata.combining(c))


def tokenize(city):
    city = city.replace("-", " ")

    return city.split()


def permutate(city_tokens):
    def number_adder(tok):
        yield tok
        yield tok + "5"
        yield tok + "10"

    if len(city_tokens) == 1:
        yield from number_adder(city_tokens[0])
        return

    yield from number_adder("".join(city_tokens))

    for token in city_tokens:
        yield from number_adder(token)


def all_permutations():
    for city in read_cities():
        for per in permutate(tokenize(normalize(city))):
            yield per


def is_valid(code):
    req = requests.post(
        "https://www.alza.cz/Services/EShopService.svc/InsertDiscountCode",
        data=json.dumps({"code": code, "confirm": False}),
        headers={
            'Content-Type': 'application/json',
            "User-Agent": (
                "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:44.0) "
                "Gecko/20100101 Firefox/44.0"
            ),
        },
    )

    data = req.json()

    is_invalid = u"není platný" in data.get("d", {}).get("Message", "")
    items_count = data.get("d", {}).get("ItemsCount", 0)

    return not is_invalid or items_count > 0


def add_valid(code):
    with open(VALID_FN, "a") as f:
        f.write(code + "\n")


def add_invalid(invalid_code):
    with open(INVALID_FN, "a") as f:
        f.write(invalid_code + "\n")


def load_invalids():
    """
    This is kinda important, because connections hangs / timeouts from time to
    time and this will keep the progress.
    """
    if not os.path.exists(INVALID_FN):
        return set()

    with open(INVALID_FN) as f:
        return set(f.read().splitlines())


# Main program ================================================================
if __name__ == '__main__':
    invalids = load_invalids()
    valid_codes = []

    for code in tqdm(all_permutations()):
        if code in invalids:
            continue

        if is_valid(code):
            add_valid(code)
            valid_codes.append(code)
        else:
            add_invalid(code)
            invalids.add(code)

    if valid_codes:
        print("Valid codes:")
        print("\t" + "\n\t".join(valid_codes))
        print("\n\nSee also `valid_codes.txt`")
    else:
        print("Sorry, no valid codes found.")
