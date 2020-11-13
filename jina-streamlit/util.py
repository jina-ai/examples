#!/usr/bin/env python3

import requests
import sys
import os
from pprint import pprint

default_phrase = "hey, dude"
default_top_k = 10


def get_results(query="", top_k=default_top_k):
    headers = {
        "Content-Type": "application/json",
    }

    data = f'{{"top_k": {top_k}, "mode": "search", "data": ["text:{query}"]}}'

    response = requests.post(
        "http://0.0.0.0:45678/api/search", headers=headers, data=data
    )

    content = response.json()
    results = []
    results_raw = content["search"]["docs"][0]["topkResults"]
    for result in results_raw:
        text = result["matchDoc"]["text"]
        results.append(text)

    return results


def render_results(results: list) -> str:
    header = """
    | Name | Line |
    | ---  | ---  |
    """
    output = header
    for text in results:
        character, words = text.split("[SEP]")
        result_text = f"| **{character}** | {words} |\n"
        output += result_text

    return output
