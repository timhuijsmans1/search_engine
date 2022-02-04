import re

from nltk.stem import PorterStemmer


class Preprocessing:
    def __init__(self):
        self.stemmer = PorterStemmer()
        stopwords = read_text_file("englishST.txt")
        self.stopwords = self.preprocess_stopwords(stopwords)

    def remove_stopwords(self, file):
        stopwords_set = set(self.stopwords)
        file_without_stopwords = [x for x in file if x not in stopwords_set]
        return file_without_stopwords

    def preprocess_stopwords(self, stopwords):
        stopwords = [x.rstrip() for x in stopwords]  # remove trailing space
        stopwords = [x.lower() for x in stopwords]  # lowercase
        return stopwords

    def preprocess_query(self, query):
        query = query.split(" ")  # split on blank space to separate terms
        query = [self.stemmer.stem(term) for term in query]  # stem every term in the query
        query = self.remove_stopwords(query)
        return query

    def tokenize_text_file(self, text_file):
        tokenized_file = []
        if isinstance(text_file, str):  # Checking whether input is only a string or a text-file
            text_file = re.findall(r'[¢£€\w]+', text_file)
            return text_file
        for i in range(len(text_file)):
            line = text_file[i]
            line = re.findall(r'[\w]+', line)
            tokenized_file.append(line)
        return tokenized_file

    def case_folding(self, tokenized_file):
        if isinstance(tokenized_file[0], list):  # Checking whether input is a list or a string as this influences the
            # list comprehension code format
            case_folded_file_comprehension = [x.lower() for line in tokenized_file for x in line]
            return case_folded_file_comprehension
        case_folded_file_comprehension = [x.lower() for x in tokenized_file]
        return case_folded_file_comprehension

    def apply_stemming(self, file):
        file = [self.stemmer.stem(x) for x in file]
        return file

    def apply_preprocessing(self, file):
        """
        Function to process text in a more suitable format
        Applies tokenization, case-folding, stopwords removal and stemming
        """
        file = self.tokenize_text_file(file)
        file = self.case_folding(file)
        file = self.remove_stopwords(file)
        file = self.apply_stemming(file)
        return file


def read_text_file(filepath):
    with open(filepath) as f:
        lines = f.readlines()
        return lines
