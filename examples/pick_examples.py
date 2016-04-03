#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Interpreter version: python 3
#
# Imports =====================================================================
import re


# Functions & classes =========================================================
def read_data():
    with open("raw_data.txt") as f:
        return f.read()


def pick_examples(raw_data):
    return [
        x
        for x in re.findall(r"[\dA-Z]{10}", raw_data)
        if not x.isdigit()
    ]


# Main program ================================================================
if __name__ == '__main__':
    examples = "\n".join(pick_examples(read_data()))
    print(examples)
