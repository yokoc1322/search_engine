import json
from utils import create_ngram, get_data_path
from index_type import Postings
from pprint import pprint
from typing import Set, Type, TypedDict, List, Dict, Optional

GRAM = 2


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


def phrase_search(query_text: str, index: Postings) -> Set[str]:
    query_grams = create_ngram(GRAM, query_text)
    Intermidiate = Dict[str, List[int]]   # docID: positions

    intermidiate: Optional[Intermidiate] = None
    for term in query_grams:
        next_intermidiate: Intermidiate = {}
        # 最初は出たやつすべて記録
        if intermidiate is None:
            if term not in index:
                return set()
            for docID in index[term]['docs'].keys():
                next_intermidiate[docID] = index[term]['docs'][docID]['position']
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

                prev_positions = intermidiate[docID]
                continue_positions = []
                for np in next_positions:
                    for pp in prev_positions:
                        if np - pp == 1:
                            continue_positions.append(np)
                            break
                if len(continue_positions) != 0:
                    next_intermidiate[docID] = continue_positions

        intermidiate = next_intermidiate

    return set(intermidiate.keys()) if intermidiate is not None else set()


if __name__ == '__main__':
    index = load_index()
    # ret = normal_search("ジョバンニ", index)
    ret = phrase_search("ジョバンニ", index)
    pprint(ret)
