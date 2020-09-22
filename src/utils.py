from typing import List
from pathlib import Path


def create_ngram(n: int, text: str) -> List[str]:
    until = len(text) - (n - 1)

    terms: List[str] = []
    for i in range(until):
        terms.append(text[i:i+n])
    return terms


def get_data_path() -> Path:
    return Path(__file__).resolve().parents[1] / 'data'
