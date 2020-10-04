import json
import math
import sqlite3
from pathlib import Path
from typing import Dict, Tuple, List
from pprint import pprint

from index_type import Doc, PostingDoc, Postings, DBPosting, DBPostingRaw
from utils import create_ngram, get_data_path
from constants import GRAM, INDEX_TABLE_NAME, DB_FILE_NAME, JSON_DIR_NAME

data_dir_path = get_data_path()
db_path = data_dir_path / DB_FILE_NAME

SQLValue = Tuple[str, str, float, str]  # term, doc_id, tf_idf, positions(json)
SQLValues = List[SQLValue]


def read_json(path: Path) -> Doc:
    with open(path, 'r', encoding='utf-8') as file:
        text = file.read()
    return json.loads(text)


def init_index():
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS {}
            (
                term TEXT,
                doc_id TEXT,
                tf_idf REAL NOT NULL,
                positions TEXT NOT NULL,
                PRIMARY KEY (term, doc_id)
            )
        """.format(INDEX_TABLE_NAME))
        c.execute("""
            CREATE INDEX IF NOT EXISTS termindex on {}(term)
        """.format(INDEX_TABLE_NAME))
        conn.commit()


def add_postings():
    def create_posting_values(doc_id: str, doc: Doc) -> SQLValues:
        terms = create_ngram(GRAM, doc['content'])

        PostingPerTerm = Dict[str, DBPosting]  # [key=term]
        postings: PostingPerTerm = {}  # [key=term]:

        for i, term in enumerate(terms):
            if term not in postings:
                postings[term] = {
                    'term': term,
                    'doc_id': doc_id,
                    'tf_idf': -1,
                    'positions': []
                }
            postings[term]['positions'].append(i)

        return [
            (posting['term'], posting['doc_id'],
             posting['tf_idf'], json.dumps(posting['positions']))
            for posting in postings.values()
        ]

    def insert_postings_to_db(values: SQLValues):
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.executemany(
                "INSERT INTO {} (term, doc_id, tf_idf, positions) VALUES (?,?,?,?)".format(
                    INDEX_TABLE_NAME),
                values
            )
            conn.commit()

    origin_file_dir = data_dir_path / JSON_DIR_NAME
    json_files = list(origin_file_dir.glob('*.json'))

    values: SQLValues = []
    for file in json_files:
        doc = read_json(file)
        ret = create_posting_values(file.name, doc)
        values = [*values, *ret]
    insert_postings_to_db(values)


def scoring_tf_idf():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    TfIdfValue = Tuple[float, str, str]  # tf_idf, term, doc_id

    def get_doc_num() -> int:
        c = conn.cursor()
        sql = "SELECT COUNT(DISTINCT doc_id) FROM {}".format(INDEX_TABLE_NAME)
        ret = c.execute(sql)
        return ret.fetchone()[0]

    def get_terms():
        c = conn.cursor()
        sql = "SELECT DISTINCT term FROM {}".format(INDEX_TABLE_NAME)
        ret = c.execute(sql)
        return ret

    def get_docs_in_same_term(term):
        c = conn.cursor()
        sql = """
            SELECT
                term, doc_id, tf_idf, positions
            FROM
                {}
            WHERE
                term=?
            """.format(INDEX_TABLE_NAME)
        ret = c.execute(sql, (term,))
        return ret

    def update_tf_idf(tf_idf_values: List[TfIdfValue]):
        c = conn.cursor()
        sql = """
            UPDATE
                {}
            SET
                tf_idf=?
            WHERE
                term=? AND doc_id=?
        """.format(INDEX_TABLE_NAME)
        c.executemany(sql, tf_idf_values)
        conn.commit()

    doc_num = get_doc_num()
    terms = get_terms()

    tf_idf_values: List[TfIdfValue] = []

    for term_tuple in terms:
        term = term_tuple[0]
        docs = list(get_docs_in_same_term(term))

        df = len(docs)
        idf = math.log(doc_num / df)

        for doc in docs:
            doc_id = doc['doc_id']
            positions = json.loads(doc['positions'])
            tf = len(positions)
            tf_idf = tf * idf
            tf_idf_values.append((tf_idf, term, doc_id,))

    update_tf_idf(tf_idf_values)


if __name__ == '__main__':
    # init_index()
    # add_postings()
    scoring_tf_idf()
