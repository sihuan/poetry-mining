import os
import pickle
import json

from collections import Counter, OrderedDict
from jieba import posseg as pseg


class CutResult(object):
    """
    分词结果
    char_counter：字频统计
    rhythmic_counter 词牌名计数
    author_counter：作者计数
    word_set：词汇表
    word_counter：词汇计数
    word_property_counter_dict：词汇词性
    author_poetry_dict：解析后的结果，作者与他对应的词
    """

    def __init__(self):
        self.char_counter = Counter()
        self.author_counter = Counter()
        self.rhythmic_counter = Counter()
        self.word_set = set()
        self.word_counter = Counter()
        self.word_property_counter_dict = {}
        self.author_poetry_dict = OrderedDict()

    def add_cut_poetry(self, author, divided_lines):
        """为author_poetry_dict添加对象"""
        ctp = self.author_poetry_dict.get(author)
        if ctp is None:
            self.author_poetry_dict[author] = ""
        else:
            self.author_poetry_dict[author] += ' '
        self.author_poetry_dict[author] += ' '.join(divided_lines)


def _is_chinese(c):
    return '\u4e00' <= c <= '\u9fff'


def cut_poetry(path, saved_dir):
    """
    对全宋词分词
    :param: path: 全宋词 json 文件所在文件夹
            saved_dir: 结果存储位置
    :return:分词结果
    """
    target_file_path = os.path.join(saved_dir, 'cut_result.pkl')
    if not os.path.exists(saved_dir):
        os.mkdir(saved_dir)
    if os.path.exists(target_file_path):
        print('load existed cut result.')
        with open(target_file_path, 'rb') as f:
            result = pickle.load(f)
    else:
        print('begin cutting poetry...')
        result = CutResult()
        files= os.listdir(path)
        for file in files:
            load_dict = []
            with open(f'{path}/{file}','r') as load_f:
                load_dict = json.load(load_f)
            for song in load_dict:
                author = song['author']
                result.author_counter[author] += 1
                rhythmic = song['rhythmic']
                result.rhythmic_counter[rhythmic] += 1
                for line in song['paragraphs']:
                    divided_lines = []
                    chars = [c for c in line if _is_chinese(c)]
                    for char in chars:
                        result.char_counter[char] += 1
                    cut_line = pseg.cut(line)
                    for word, property in cut_line:
                        if not _is_chinese(word):
                            continue
                        if result.word_property_counter_dict.get(property) is None:
                            result.word_property_counter_dict[property] = Counter()
                        result.word_property_counter_dict[property][word] += 1
                        result.word_set.add(word)
                        result.word_counter[word] += 1
                        divided_lines.append(word)
                    divided_lines.append("\n")
                    result.add_cut_poetry(author, divided_lines)
        with open(target_file_path, 'wb') as f:
            pickle.dump(result, f)
    return result
