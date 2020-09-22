import json
from pathlib import Path

from utils import create_ngram, get_data_path
from index_type import Doc, Postings, PostingDoc


# docID == filename
def create_postings(docID: str, doc: Doc, postings: Postings):
    terms = create_ngram(2, doc['content'])
    for i, term in enumerate(terms):
        if term not in postings:
            postings[term] = {
                'num': 0,
                'docs': {}
            }

        if docID not in postings[term]['docs']:
            position_doc: PostingDoc = {
                'num': 0,
                'position': []
            }
            postings[term]['docs'][docID] = position_doc

        postings[term]['num'] += 1
        postings[term]['docs'][docID]['num'] += 1
        postings[term]['docs'][docID]['position'].append(i)


def read_json(path: Path) -> Doc:
    with open(path, 'r', encoding='utf-8') as file:
        text = file.read()
    return json.loads(text)


if __name__ == '__main__':
    data_dir = get_data_path()

    origin_file_dir = data_dir / 'json'
    json_files = origin_file_dir.glob('*.json')
    postings: Postings = {}

    for file in json_files:
        doc = read_json(file)
        create_postings(file.name, doc, postings)

    with open(
        data_dir / 'inverted_index.json',
        'w',
        encoding='utf-8'
    ) as index_file:
        index_file.write(json.dumps(postings, indent=2, ensure_ascii=False))
