from typing import Dict, TypedDict, List


class Doc(TypedDict):
    title: str
    author: str
    content: str


class PostingDoc(TypedDict):
    num: int
    position: List[int]


class Posting(TypedDict):
    num: int
    docs: Dict[str, PostingDoc]  # [key=docID]


Postings = Dict[str, Posting]  # [key=term]
