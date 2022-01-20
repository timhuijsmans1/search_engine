import math
from functools import reduce
import xml.etree.ElementTree as ET

from preprocessing import Preprocessing
from functions import read_index_from_file, create_doc_dictionary
from functions import get_term_entry_from_inverted_index
from functions import extract_all_documents_term_appears_in


class Vsm_model:

    def compute_weight_term_document(self, term, document, positional_inverted_index, documents_appearing_in, N):
        """
        Function to compute the term weight based on TFIDF term weighing
        """
        if document not in positional_inverted_index[term][1]:
            w_t_d = 0
        else:
            tf = len(positional_inverted_index[term][1][document])  # how often the term appears in the current document
            tf = 1 + math.log10(tf)
            df = len(documents_appearing_in[term])
            idf = math.log10(N / df)
            w_t_d = tf * idf
        return w_t_d

    def compute_weight_term_query(self, term, query):
        """
        Slide 21 - lecture 7 - red boxes are for query
        follows lnc.ltc schema -
        """
        term_freq = query.count(term)  # how many times the term appears in the query
        tf = 1 + math.log10(term_freq)  #
        idf = 1  # as per the red boxes in the slide
        w_t_q = tf * idf
        return w_t_q

    def ranked_retrieval(self, query, pos_inverted_index, N, document_dict):
        """
        Ranked retrieval using cosine similarity algorithm
        N - total number of documents in the collection
        """

        term_inverted_indexes = {}  # Dictionary to store the entries in the inverted index of each term in the query
        documents_appearing_in = {}  # Dictionary to store the documents each term in the query appears in
        for term in query:
            term_inverted_indexes[term] = get_term_entry_from_inverted_index(pos_inverted_index, term)
            documents_appearing_in[term] = extract_all_documents_term_appears_in(term_inverted_indexes[term])
        # Find the union of docs between all terms in the query
        union_of_documents = sorted(reduce(set.union, map(set, documents_appearing_in.values())))

        document_scores = {}  # Dictionary to map document id with computed score
        for document in union_of_documents:
            score = 0
            for term in query:
                w_t_d = self.compute_weight_term_document(term, document, pos_inverted_index, documents_appearing_in, N)
                w_t_q = self.compute_weight_term_query(term, query)
                score += w_t_d * w_t_q  # multiply the two for a the score
            score = score / len(document_dict[document])  # need to get the length of the document
            document_scores[document] = score  # append the final score for each document
        sorted_document_scores = sorted(document_scores.items(), key=lambda x: x[1], reverse=True)
        sorted_document_scores = sorted_document_scores[:100]
        return sorted_document_scores

if __name__ == '__main__':
    preprocessor = Preprocessing()
    Vsm_model = Vsm_model() # Initialise class
    # Read the collection
    tree = ET.parse("trec.5000.xml")
    document_dic = create_doc_dictionary(tree, preprocessor)
    inverted_index = read_index_from_file("inverted_index.txt")
    queries = ["income tax reduction", "peace in the Middle East", "unemployment rate in UK",
               "industry in Scotland", "the industries of computers", "Microsoft Wdinows", "stock market in Japan",
               "the education with computers", "health industry", "campaigns of political parties"]
    queries = [preprocessor.preprocess_query(query) for query in queries]
    query_results_dict = {}
    N = len(document_dic)
    for i, query in enumerate(queries):
        query_results_dict[i] = Vsm_model.ranked_retrieval(query, inverted_index, N, document_dic)
    test = 0
