import json
import re

import xml.etree.ElementTree as ET

from nltk.stem.porter import *
from newspaper import Article

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

def nasdaq_processor(file_name):
    nasdaq_companes=[]
    stop_words_companies=['corp.','corp','inc','inc.','ltd.','ltd','nasdaq','stock','test','shares','N.A.']
    substrings=['.com', ',']
    holder=[]
    
    # Build list from text file
    with open(file_name) as f:
        next(f)
        for line in f:
            company=line.split('|')[1].split('-')[0].strip()
            nasdaq_companes.append(company)
    
    
    # Remove stop words and substrings
    for comp in nasdaq_companes:
        split_companies=comp.split(" ")

        for i in split_companies:

            # Remove .com,',', etc.
            for substring in substrings:
                if substring in i:
                    i=i.replace(substring,'')

            # Dont include stop words   
            if i.lower() not in (string.lower() for string in stop_words_companies):
                holder.append(i)

    # Remove single elements
    for comp in holder:
        if len(comp)<=1:
            try:
                while True:
                    holder.remove(comp)
            except ValueError:
                pass
    
    # Remove duplicates
    holder = list(dict.fromkeys(holder))
    
    return (holder)

def extract_content(url):

    try:
        article = Article(url)
        article.download()
        article.parse()

        # Add to title colum
        content= article.text
        
        return content

    except:
        return False

def check_nasdaq(nasdaq_list, text_body):
    """Check if text body contains at least one mention of nasdaq companies"""

    for word in nasdaq_list:
        if word in text_body:
            return True
    return False


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

def add_row_to_db(doc_id, title, url, date, body):
    """adds one article to the database"""
    return
    
def index_builder(url_file, nasdaq_file):
    """
    return:
    index in the encoded dictionary form 
                        {word: [document_count, [ [doc_delta, [positions]], [doc_delta, [positions]], ... ]}
    """
    inverted_index = {}
    nasdaq_list = nasdaq_processor(nasdaq_file)

    # @ part 4 of word doc
    # input = csv with doc_id, title, url, date
    with open(url_file, 'r') as f:
        next(f)
        lines = f.readlines()

    for line in lines:
        index, doc_id, title, url, date = line.split('\t')

        # get article body with library from url
        url_content = extract_content(url)

        if url_content != False:
            nasdaq_response = check_nasdaq(nasdaq_list, url_content)
            if nasdaq_response:

                # TODO
                # write to database (doc_id, title, url, date, body)

                preprocessing = Preprocessing()
                pre_processed_article = preprocessing.apply_preprocessing(url_content)

                inverted_index = index_extender(pre_processed_article, inverted_index, int(doc_id))

    return inverted_index

def index_writer(index):
    """
    input params:
    inverted_index_dictionary : dictionary
        index in the encoded dictionary form 
                                {word: [document_count, [ [doc_delta, [positions]], [doc_delta, [positions]], ... ]}

    return:
    index file
    hash table word2byte_location
    """
    word2bytes = {}
    with open("index.json", 'w') as f:
        for word in index:
            start_byte = f.tell()

            # write k,v to file
            dict_to_write = {word: index[word]}
            string = json.dumps(dict_to_write)
            f.write(string)
            end_byte = f.tell()
            bytes_to_read = end_byte - start_byte
            byte_values = (start_byte, bytes_to_read)
            word2bytes[word] = byte_values

    return word2bytes

def delta_decoder(delta_encoded_inverted_list, word):
    """
    input params:
    v_byte_encoded_inverted_list : dictionary
        one key being the word, and values a list with delta encoded doc_id and decoded positions

    return:
    inverted list in its original format {word: [document_count, [[doc_number, [positions]]]}
    """

    doc_count, doc_numbers = delta_encoded_inverted_list[word]

    dict_out = {word: [doc_count, {}]}

    # add the first doc number manually
    doc_number, positions = doc_numbers[0]
    dict_out[word][1][doc_number] = positions

    # loop over all but the first doc_numbers, first is not encoded
    for i in range(1, len(doc_numbers)):
        doc_number = sum([doc_tuple[0] for doc_tuple in doc_numbers[:i + 1]]) # calculate the doc number for each delta
        positions = doc_numbers[i][1]
        dict_out[word][1][doc_number] = positions
    return dict_out

def retrieval(word_list, word2byte, index_path):
    """
    input params:
    word_list : list
        list of pre-processed words in the query
    word2byte : dictionary
        dictionary with collection vocabulary as keys and index byte start and size as value

    return:
    mini index in original format, only containing those inverted lists that are relevant to the query: 
                        {word: [document_count, [ [doc_number, [positions]], [doc_number, [positions]], ... ]}
    """
    mini_index = {}
    
    with open(index_path, 'r') as f:
        for word in word_list:
            try: # if query word is in our vocabulary
                start_byte = word2byte[word][0]
                bytes_to_read = word2byte[word][1]

                # find the bytes where we need to start reading
                f.seek(start_byte)
                inverted_list = f.read(bytes_to_read)

                # add inverted list to the index we want to retrieve
                inverted_list_dict = json.loads(inverted_list)
                decoded_inverted_list = delta_decoder(inverted_list_dict, word)
                mini_index = {**mini_index, **decoded_inverted_list}
            except:
                pass # if query word is not in our vocabulary
    
    return mini_index

def word2byte_writer(word2byte_dict):
    with open("word2byte.json", 'w') as f:
        json.dump(word2byte_dict, f)

if __name__ == "__main__":
    URL_FILE = "5_article_test.tsv"
    NASDAQ_FILE = "nasdaq_companies.txt"

    # this function builds the inverted index in dictionary form
    inverted_index_final = index_builder(URL_FILE, NASDAQ_FILE)

    # this function writes the index to memory and returns the byte offset hash
    word2byte = index_writer(inverted_index_final)

    # this function writes the byte offset hash to disk
    word2byte_writer(word2byte)
