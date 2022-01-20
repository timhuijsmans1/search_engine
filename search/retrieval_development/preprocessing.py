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
        query = query.split(" ") # split on blank space to separate terms
        query = [self.stemmer.stem(term) for term in query] # stem every term in the query
        query = self.remove_stopwords(query)
        return query


def read_text_file(filepath):
    with open(filepath) as f:
        lines = f.readlines()
        return lines