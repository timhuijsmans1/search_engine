import re
import json

from nltk.stem import PorterStemmer
from google.cloud import storage
#from search.retrieval.retrieval_helpers.helpers import read_text_file  # - used for testing on Vlad's machine


class Preprocessing:
    def __init__(self, deployment):
        self.stemmer = PorterStemmer()          
        stopwords = self.json_loader("englishST.json", deployment)
        self.stopwords = self.preprocess_stopwords(stopwords)

    def is_phrase_bool(self, query):
        if '"' in query:
            return True
        else:
            return False

    def json_loader(self, file_name, deployment):
        if deployment:
            # retrieve json string from cloud storage
            client = storage.Client()
            bucket = client.get_bucket('ttds2-338418.appspot.com')
            blob = bucket.get_blob(file_name)
            json_string = blob.download_as_string()

            output = json.loads(json_string)
        else:
            path = os.path.join("retrieval/data", file_name)
            with open(path, "r") as f:
                output = json.load(f)
        return output

    def remove_stopwords(self, file):
        stopwords_set = set(self.stopwords)
        file_without_stopwords = [x for x in file if x not in stopwords_set]
        return file_without_stopwords

    def preprocess_stopwords(self, stopwords):
        stopwords = [x.rstrip() for x in stopwords]  # remove trailing space
        stopwords = [x.lower() for x in stopwords]  # lowercase
        return stopwords

    def preprocess_query(self, query, is_proximity_query=False):
        if is_proximity_query:
            proximity_value, term1, term2 = self.preprocess_proximity_query()
            return proximity_value, term1, term2

        query = query.split(" ")  # split on blank space to separate terms
        query = [self.stemmer.stem(term) for term in query]  # stem every term in the query
        query = self.remove_stopwords(query)
        return query

    def preprocess_proximity_query(self, query):
        proximity_value, term1, term2 = re.findall('[a-zA-Z0-9]+', query)
        proximity_value = int(proximity_value)
        term1 = self.stemmer.stem(term1)
        term2 = self.stemmer.stem(term2)
        preprocessed_query = [[term1, term2]]
        return proximity_value, preprocessed_query

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

    def preprocess_boolean_query(self, query, boolean_operators):
        position_with_parantheses = []
        terms = []
        i = 0  # keeping track of position of query term
        identified_start_of_phrase = False
        for term in query.split():
            if term not in boolean_operators:
                if '(' in term:
                    position_with_parantheses.append(i)
                if self.is_phrase_bool(term) and not identified_start_of_phrase:  # does this have quotes in it and first time we see it?
                    phrase = []
                    identified_start_of_phrase = True
                    term = self.clean_term(term)
                    phrase.append(term)
                elif identified_start_of_phrase:
                    if self.is_phrase_bool(term):
                        identified_start_of_phrase = False
                    term = self.clean_term(term)
                    phrase.append(term)
                    if not identified_start_of_phrase:
                        terms.append(phrase)
                else:
                    term = [self.clean_term(term)]
                    terms.append(term)
                i+=1
        return terms, boolean_operators, position_with_parantheses

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


    def clean_term(self, term):
        term = re.sub('[^a-zA-Z]+', '', term)
        term = self.stemmer.stem(term)
        return term
