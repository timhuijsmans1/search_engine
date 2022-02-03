import math
from functools import reduce
import xml.etree.ElementTree as ET
import numpy as np
import json

from preprocessing import Preprocessing


class bm25_model:

    def extract_all_documents_term_appears_in(self, inverted_index_term):

        documents_term_appears_in = []
        for k, v in inverted_index_term[1].items():
            documents_term_appears_in.append(k)
        return documents_term_appears_in

    def compute_weight_term_document(self, term, document, positional_inverted_index, documents_appearing_in, N,
                                     doc_size):

        l_tot = 0
        l_avg = 0
        k = 1.5

        for d in doc_size.values():
            l_tot += d

        l_avg = l_tot / N

        if document not in positional_inverted_index[term].keys():
            w_t_d = 0
        else:
            tf = len(positional_inverted_index[term][document])

            df = len(documents_appearing_in[term])
            idf = math.log(1 + ((N - df + 0.5) / (df + 0.5)))
            d = doc_size[document] / l_avg
            w_t_d = idf * (tf / ((k * d) + tf + 0.5))
        return w_t_d

    def get_term_entry_from_inverted_index(self, inverted_index, term):

        if term in inverted_index.keys():
            inverted_index_term = inverted_index[term]
            return inverted_index_term

    def extract_all_documents_term_appears_in(self, inverted_index_term):

        documents_term_appears_in = []
        for k in inverted_index_term.keys():
            documents_term_appears_in.append(k)
        return documents_term_appears_in

    def rank(self, query, inv_ind, N, doc_size):

        term_inverted_indexes = {}
        documents_appearing_in = {}

        for term in query:
            term_inverted_indexes[term] = self.get_term_entry_from_inverted_index(inv_ind, term)
            documents_appearing_in[term] = self.extract_all_documents_term_appears_in(term_inverted_indexes[term])


        union_of_documents = sorted(reduce(set.union, map(set, documents_appearing_in.values())))

        document_scores = {}  # Dictionary to map document id with computed score

        for document in union_of_documents:

            score = 0
            document_vector = []

            for term in query:
                w_t_d = self.compute_weight_term_document(term, document, inv_ind, documents_appearing_in, N, doc_size)
                document_vector.append(w_t_d)
                score += w_t_d

            document_scores[document] = score

        sorted_document_scores = sorted(document_scores.items(), key=lambda x: x[1], reverse=True)
        sorted_document_scores = sorted_document_scores[:100]
        return sorted_document_scores


if __name__ == '__main__':
    preprocessor = Preprocessing()
    bm25_model = bm25_model()

    with open('result.json') as results:
        with open('content_length.json') as docs:
            inv_ind = json.load(results)
            doc_size = json.load(docs)

            query = input("Enter query: ")
            query = preprocessor.preprocess_query(query)
            query_results_dict = {}
            N = len(doc_size.keys())
            query_results_dict = bm25_model.rank(query, inv_ind, N, doc_size)
            print(query_results_dict)
