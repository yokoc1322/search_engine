import json
from typing import Dict, TypedDict
from pathlib import Path

from utils import create_ngram, get_data_path


class Doc(TypedDict):
    title: str
    author: str
    content: str


class PostingDoc(TypedDict):
    num: int


class Posting(TypedDict):
    num: int
    docs: Dict[str, PostingDoc]  # [key=docID]


Postings = Dict[str, Posting]  # [key=term]


# docID == filename
def create_postings(docID: str, doc: Doc, postings: Postings):
    terms = create_ngram(2, doc['content'])
    for term in terms:
        if term not in postings:
            postings[term] = {
                'num': 0,
                'docs': {}
            }

        if docID not in postings[term]['docs']:
            postings[term]['docs'][docID] = {
                'num': 0
            }

        postings[term]['num'] += 1
        postings[term]['docs'][docID]['num'] += 1


def read_json(path: Path) -> Doc:
    with open(path, 'r', encoding='utf-8') as file:
        text = file.read()
    return json.loads(text)


data_dir = get_data_path()

origin_file_dir = data_dir / 'json'
json_files = origin_file_dir.glob('*.json')
postings: Postings = {}

for file in json_files:
    doc = read_json(file)
    create_postings(file.name, doc, postings)

with open(data_dir / 'inverted_index.json', 'w', encoding='utf-8') as index_file:
    index_file.write(json.dumps(postings, indent=2, ensure_ascii=False))
