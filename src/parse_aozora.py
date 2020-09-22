import json
import re
from pathlib import Path, WindowsPath
from random import randrange
from typing import List, TypedDict

from bs4 import BeautifulSoup

from utils import get_data_path


class Doc(TypedDict):
    title: str
    author: str
    content: str


def listup_content_path() -> List[Path]:
    parent = WindowsPath('D:/aozorabunko/cards')
    files = list(parent.glob('**/*.html'))

    # 適当にピック
    RAND_MAX = 300
    DOUBLE_PICK_THR = 10
    count = 0
    until = randrange(1, RAND_MAX)
    pickup_files = []
    for file in files:
        if until == count:
            until = randrange(1, RAND_MAX)
            if until % DOUBLE_PICK_THR == 0:  # たまには2つ連続で取りたい
                until = 1
            pickup_files.append(file)
            count = 0
        count += 1
    return pickup_files


def content_to_json(input_file, output) -> None:
    try:
        with open(input_file, 'r', encoding='shift-jis') as file:
            html_doc = file.read()
            html_doc = html_doc.replace('　', '')  # 全角空白
            html_doc = re.sub('<ruby>.*</ruby>', '', html_doc)

            soup = BeautifulSoup(html_doc, features="html.parser")

            title = soup.find(class_="title").text
            author = soup.find(class_="author").text
            content = soup.find(class_="main_text").text

            doc = {
                'title': title,
                'author': author,
                'content': content.replace('\n', '')
            }

        with open(output, 'w', encoding='utf-8') as file:
            file.write(json.dumps(doc, ensure_ascii=False))
    except:
        print("Error!")
        print(input_file)


data_dir = get_data_path()
files = listup_content_path()
files_with_output = [
    {
        'in': filepath,
        'out': data_dir / 'json' / (filepath.name + '.json')}
    for filepath in files
]
for f in files_with_output:
    content_to_json(f['in'], f['out'])
