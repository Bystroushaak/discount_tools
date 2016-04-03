#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Interpreter version: python 3
#
"""
Tento script stojí na mé zkušenosti s 5% slevovým kódem na alzu FRYDEK5. Z toho
jsem vyvodil hypotézu, že by mohlo existovat více slevových kódů nazvaných
podle měst v Čechách.
"""
#
# Imports =====================================================================
import os.path
import unicodedata


# Functions & classes =========================================================
def read_cities():
    fn = os.path.join(os.path.dirname(__file__), "mesta.txt")
    with open(fn) as f:
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


# Main program ================================================================
if __name__ == '__main__':
    for code in all_permutations():
        print(code)
