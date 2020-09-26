import json
from pprint import pprint
from typing import List, Dict, List, Optional, Set, Type, TypedDict

from index_type import Postings
from utils import create_ngram, get_data_path

GRAM = 2


class IntermidiateDoc(TypedDict):
    positions: List[int]
    sum_tf_idf: float


class SearchResultItem(TypedDict):
    doc_id: str
    sum_tf_idf: float


def load_index() -> Postings:
    data_dir = get_data_path()
    with open(data_dir / 'inverted_index.json', 'r', encoding='utf-8') as file:
        content = file.read()
        return json.loads(content)


def search(query_text: str, index: Postings) -> List[SearchResultItem]:
    query_grams = create_ngram(GRAM, query_text)
    Intermidiate = Dict[str, IntermidiateDoc]   # [key=doc_id]

    intermidiate: Optional[Intermidiate] = None
    for term in query_grams:
        next_intermidiate: Intermidiate = {}
        # 最初は出たやつすべて記録
        if intermidiate is None:
            if term not in index:
                return set()
            for doc_id in index[term]['docs'].keys():
                next_intermidiate[doc_id] = {
                    'positions': index[term]['docs'][doc_id]['position'],
                    'sum_tf_idf': index[term]['docs'][doc_id]['tf_idf']
                }
        # 2回目以降は、以前のternと離れてないやつを残していく
        else:
            # 単語が見つからない
            if term not in index:
                return set()
            for doc_id in index[term]['docs'].keys():
                next_positions = index[term]['docs'][doc_id]['position']

                # まだ一度も出て生きていない単語
                if doc_id not in intermidiate:
                    continue

                prev_positions = intermidiate[doc_id]['positions']
                continue_positions = []
                for np in next_positions:
                    for pp in prev_positions:
                        if np - pp == 1:
                            continue_positions.append(np)
                            break
                if len(continue_positions) != 0:
                    current_tf_idf = intermidiate[doc_id]['sum_tf_idf']
                    next_intermidiate[doc_id] = {
                        'positions': continue_positions,
                        'sum_tf_idf': current_tf_idf + index[term]['docs'][doc_id]['tf_idf']
                    }

        intermidiate = next_intermidiate

    if intermidiate is not None:
        intermidiate_list = [
            {
                'doc_id': doc_id,
                'sum_tf_idf': intermidiate[doc_id]['sum_tf_idf']

            } for doc_id in intermidiate
        ]

        intermidiate_list.sort(key=lambda doc: doc['sum_tf_idf'], reverse=True)
        return intermidiate_list
    else:
        return []


if __name__ == '__main__':
    index = load_index()
    # ret = search("ジョバンニ", index)
    ret = search("こんにちは", index)
    pprint(ret)
