#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import sys
import json
import copy
import os.path
import argparse

from tqdm import tqdm
import requests
if hasattr(requests, "packages"):
    requests.packages.urllib3.disable_warnings()


# Variables ===================================================================
VALID_FN = "valid_codes.txt"
INVALID_FN = "invalid_codes.txt"


# Functions & classes =========================================================
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
    msg = data.get("d", {}).get("Message", "")

    is_used = u"byl již použit" in msg
    is_invalid = u"není platný" in msg
    items_count = data.get("d", {}).get("ItemsCount", 0)

    return not (is_invalid or is_used) or items_count > 0


def save_valid(code):
    with open(VALID_FN, "a") as f:
        f.write(code + "\n")


def save_invalid(invalid_code):
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


def process_codes(codes, invalids):
    invalids = copy.copy(invalids)
    valid_codes = []

    for code in codes:
        code = code.strip()

        if not code:
            continue

        if code in invalids:
            continue

        if is_valid(code):
            valid_codes.append(code)
            if args.save:
                save_valid(code)
        else:
            invalids.add(code)
            if args.save:
                save_invalid(code)

    return valid_codes, invalids


# Main program ================================================================
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Test alza gift / discount code."
    )
    parser.add_argument(
        "CODES",
        nargs="*",
        help="List of codes. Use - to read codes from stdin."
    )
    parser.add_argument(
        "-s",
        "--save",
        action="store_true",
        help="Save progress."
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Don't use progressbar."
    )

    args = parser.parse_args()

    # prepare dataset
    dataset = args.CODES if args.CODES else sys.stdin
    dataset = dataset if args.quiet else tqdm(dataset)

    invalids = load_invalids() if args.save else set()

    valid_codes, invalids = process_codes(dataset, invalids)

    if not valid_codes:
        print("Sorry, no valid codes found.")
        sys.exit(1)

    if not args.quiet:
        print("Valid codes:")

    sep = "\t" if not args.quiet else ""

    print(sep + ("\n" + sep).join(valid_codes))

    if args.save and not args.quiet:
        print("\nSee also `valid_codes.txt`")
