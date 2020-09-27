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
    docs: Dict[str, PostingDoc]  # [key=doc_id]
    idf: float


Postings = Dict[str, Posting]  # [key=term]


class DBPosting(TypedDict):
    term: str
    doc_id: str
    tf_idf: float
    positions: List[int]


class DBPostingRaw(TypedDict):
    term: str
    doc_id: str
    tf_idf: float
    positions: str  # jsonのlist
