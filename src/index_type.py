from typing import Dict, TypedDict, List


class Doc(TypedDict):
    title: str
    author: str
    content: str


class PostingDoc(TypedDict, total=False):
    num: int
    position: List[int]
    tf: int
    tf_idf: float


class Posting(TypedDict, total=False):
    num: int
    docs: Dict[str, PostingDoc]  # [key=docID]
    idf: float


Postings = Dict[str, Posting]  # [key=term]
