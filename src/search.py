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
    docID: str
    sum_tf_idf: float


def load_index() -> Postings:
    data_dir = get_data_path()
    with open(data_dir / 'inverted_index.json', 'r', encoding='utf-8') as file:
        content = file.read()
        return json.loads(content)


def normal_search(query_text: str, index: Postings) -> Set[str]:
    query_grams = create_ngram(GRAM, query_text)

    candidate = set()
    for term in query_grams:
        next_candidate = set()
        if term not in index:
            break
        for k in index[term]['docs'].keys():
            next_candidate.add(k)
        candidate = candidate.union(next_candidate)
    return candidate


def phrase_search(query_text: str, index: Postings) -> List[SearchResultItem]:
    query_grams = create_ngram(GRAM, query_text)
    Intermidiate = Dict[str, IntermidiateDoc]   # [key=docID]

    intermidiate: Optional[Intermidiate] = None
    for term in query_grams:
        next_intermidiate: Intermidiate = {}
        # 最初は出たやつすべて記録
        if intermidiate is None:
            if term not in index:
                return set()
            for docID in index[term]['docs'].keys():
                next_intermidiate[docID] = {
                    'positions': index[term]['docs'][docID]['position'],
                    'sum_tf_idf': index[term]['docs'][docID]['tf_idf']
                }
        # 2回目以降は、以前のternと離れてないやつを残していく
        else:
            # 単語が見つからない
            if term not in index:
                return set()
            for docID in index[term]['docs'].keys():
                next_positions = index[term]['docs'][docID]['position']

                # まだ一度も出て生きていない単語
                if docID not in intermidiate:
                    continue

                prev_positions = intermidiate[docID]['positions']
                continue_positions = []
                for np in next_positions:
                    for pp in prev_positions:
                        if np - pp == 1:
                            continue_positions.append(np)
                            break
                if len(continue_positions) != 0:
                    current_tf_idf = intermidiate[docID]['sum_tf_idf']
                    next_intermidiate[docID] = {
                        'positions': continue_positions,
                        'sum_tf_idf': current_tf_idf + index[term]['docs'][docID]['tf_idf']
                    }

        intermidiate = next_intermidiate

    if intermidiate is not None:
        intermidiate_list = [
            {
                'docID': docID,
                'sum_tf_idf': intermidiate[docID]['sum_tf_idf']

            } for docID in intermidiate
        ]

        intermidiate_list.sort(key=lambda doc: doc['sum_tf_idf'], reverse=True)
        return intermidiate_list
    else:
        return []


if __name__ == '__main__':
    index = load_index()
    # ret = normal_search("ジョバンニ", index)
    # ret = phrase_search("ジョバンニ", index)
    ret = phrase_search("こんにちは", index)
    pprint(ret)
