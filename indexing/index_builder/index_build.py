import re
from nltk.stem.porter import *

class Preprocessing:
    def __init__(self, stop_file_path):
        self.stemmer = PorterStemmer()
        stopwords = read_text_file(stop_file_path)
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

def index_extender(text_body, index, doc_number):
    """
    input params:
    text_body : list
        list of all the pre-processed tokens in a text body
    index : dictionary
        the current index with lists delta and v-byte encoded

    return:
    extended index in the following format: 
                        {word: [document_count, [ [doc_delta, [positions]], [doc_delta, [positions]], ... ]}
    """

    for position, word in enumerate(text_body):

        if word in index:

            # sums deltas to find the most recently added doc number of the current word.
            last_doc_number = sum([doc_tuple[0] for doc_tuple in index[word][1]])
            delta = doc_number - last_doc_number

            # only add the position to the position list of the existing document number entry
            if doc_number == last_doc_number: 
                index[word][1][-1][1].append(position + 1) 
            # add new doc number/position list to inverted list
            else:
                index[word][1].append([delta, [position + 1]])
                index[word][0] += 1
        # build the initial list of doc/pos combos, no delta encoding on this iteration
        else:
            index[word] = [1, [[doc_number, [position + 1]]]]

    return index

def index_builder(content_file, stop_word_file_path):
    """
    return:
    index in the encoded dictionary form 
                        {word: [document_count, [ [doc_delta, [positions]], [doc_delta, [positions]], ... ]}
    """
    inverted_index = {}

    # @ part 4 of word doc
    # input = csv with doc_id, title, url, date
    with open(content_file, 'r') as f:
        while True:
            line = f.readline()
            if not line:
                break

            doc_id, title, body, url, date = line.split('\t')

            # TODO
            # write to database (doc_id, title, url, date, body)

            preprocessing = Preprocessing(stop_word_file_path)
            pre_processed_article = preprocessing.apply_preprocessing(body)

            inverted_index = index_extender(pre_processed_article, inverted_index, int(doc_id))

    return inverted_index