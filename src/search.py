import json
import sqlite3
from pprint import pprint
from typing import Dict, List, Optional, Set, Type, TypedDict

from constants import DB_FILE_NAME, GRAM, INDEX_TABLE_NAME
from index_type import DBPosting, Postings
from utils import create_ngram, get_data_path

data_dir_path = get_data_path()
db_path = data_dir_path / DB_FILE_NAME


class IntermidiateDoc(TypedDict):
    positions: List[int]
    sum_tf_idf: float


class SearchResultItem(TypedDict):
    doc_id: str
    sum_tf_idf: float


Intermidiate = Dict[str, IntermidiateDoc]  # [key=doc_id]


def search(query_text: str) -> List[SearchResultItem]:
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row

        def get_docs_by_term(term: str) -> List[DBPosting]:
            c = conn.cursor()
            db_docs = c.execute("""
                SELECT term, doc_id, tf_idf, positions
                FROM {}
                WHERE term=?
            """.format(INDEX_TABLE_NAME), (term,))
            return [{
                'term': doc['term'],
                'doc_id': doc['doc_id'],
                'tf_idf': doc['tf_idf'],
                'positions': json.loads(doc['positions'])
            } for doc in db_docs]

        query_grams = create_ngram(GRAM, query_text)

        intermidiate: Optional[Intermidiate] = None
        for term in query_grams:
            next_intermidiate: Intermidiate = {}
            docs = get_docs_by_term(term)

            if intermidiate is None:
                for doc in docs:
                    next_intermidiate[doc['doc_id']] = {
                        'positions': doc['positions'],
                        'sum_tf_idf': doc['tf_idf']
                    }
            else:
                for doc in docs:
                    doc_id = doc['doc_id']
                    positions = doc['positions']
                    tf_idf = doc['tf_idf']

                    # まだ一度も出てきていない単語
                    if doc_id not in intermidiate:
                        continue

                    prev_positions = intermidiate[doc_id]['positions']
                    continue_positions = []
                    for p in positions:
                        for pp in prev_positions:
                            if p - pp == 1:
                                continue_positions.append(p)
                                break
                    if len(continue_positions) != 0:
                        prev_tf_idf = intermidiate[doc_id]['sum_tf_idf']
                        next_intermidiate[doc_id] = {
                            'positions': continue_positions,
                            'sum_tf_idf': prev_tf_idf + tf_idf
                        }

            intermidiate = next_intermidiate

        if intermidiate is not None:
            intermidiate_list = [
                {
                    'doc_id': doc_id,
                    'sum_tf_idf': intermidiate[doc_id]['sum_tf_idf']

                } for doc_id in intermidiate
            ]
            intermidiate_list.sort(
                key=lambda doc: doc['sum_tf_idf'], reverse=True)
            return intermidiate_list
        else:
            return []


if __name__ == '__main__':
    # ret = search("ジョバンニ")
    ret = search("こんにちは")
    pprint(ret)
