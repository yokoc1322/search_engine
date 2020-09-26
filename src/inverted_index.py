import json
import math
from pathlib import Path

from utils import create_ngram, get_data_path
from index_type import Doc, Postings, PostingDoc


# doc_id == filename
def create_postings(doc_id: str, doc: Doc, postings: Postings):
    terms = create_ngram(2, doc['content'])
    for i, term in enumerate(terms):
        if term not in postings:
            postings[term] = {
                'num': 0,
                'docs': {}
            }

        if doc_id not in postings[term]['docs']:
            position_doc: PostingDoc = {
                'num': 0,
                'position': []
            }
            postings[term]['docs'][doc_id] = position_doc

        postings[term]['num'] += 1
        postings[term]['docs'][doc_id]['num'] += 1
        postings[term]['docs'][doc_id]['position'].append(i)


def read_json(path: Path) -> Doc:
    with open(path, 'r', encoding='utf-8') as file:
        text = file.read()
    return json.loads(text)


def add_tf_idf_score(postings: Postings, doc_num: int):
    for _, posting in postings.items():
        posting['idf'] = math.log(doc_num/len(posting['docs']), 10)

        for _, posting_doc in posting['docs'].items():
            posting_doc['tf'] = len(posting_doc['position'])
            posting_doc['tf_idf'] = posting_doc['tf'] * posting['idf']


if __name__ == '__main__':
    data_dir = get_data_path()

    origin_file_dir = data_dir / 'json'
    json_files = list(origin_file_dir.glob('*.json'))
    postings: Postings = {}

    for file in json_files:
        doc = read_json(file)
        create_postings(file.name, doc, postings)

    add_tf_idf_score(postings, len(json_files))

    with open(
        data_dir / 'inverted_index.json',
        'w',
        encoding='utf-8'
    ) as index_file:
        index_file.write(json.dumps(postings, indent=2, ensure_ascii=False))
