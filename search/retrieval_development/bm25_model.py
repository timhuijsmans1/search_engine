import math
from functools import reduce
import re
import xml.etree.ElementTree as ET
import numpy as np
import json
from collections import defaultdict, OrderedDict

from preprocessing import Preprocessing


class bm25_model:


    def compute_weight_term_document(self, term, document, positional_inverted_index, documents_appearing_in, N,
                                     doc_size):

        l_tot = 0
        l_avg = 0
        k = 1.5

        for d in doc_size.values():
            l_tot += int(float(d))

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

    def compute_weight_phrase_document(self, document, tf, df, N,
                                     doc_size):
        l_tot = 0
        l_avg = 0
        k = 1.5

        for d in doc_size.values():
            l_tot += int(float(d))

        l_avg = l_tot / N
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

    def consecutive_occ(self, inverted_index_doc):

        tot = len(inverted_index_doc)
        tot_app = sorted(sum(inverted_index_doc, [])) # Main Assumption that one word is not occurring twice in a row
        count = 0
        consecutive = 0

        for i in range(len(tot_app)-1):
            if (tot_app[i+1] - tot_app[i]) == 1:
                for t in range(tot - 1):
                    if tot_app[i] in inverted_index_doc[t] and tot_app[i+1] in inverted_index_doc[t+1]:
                        count += 1
                        if count == (tot - 1):
                            consecutive += 1
                            count = 0

            else:
                count = 0

        return consecutive



    def rank(self, query, inv_ind, N, doc_size):

        term_inverted_indexes = {}
        documents_appearing_in = {}

        for term in query:
            term_inverted_indexes[term] = self.get_term_entry_from_inverted_index(inv_ind, term)
            documents_appearing_in[term] = self.extract_all_documents_term_appears_in(term_inverted_indexes[term])

        union_of_documents = sorted(reduce(set.union, map(set, documents_appearing_in.values())))

        document_scores = {}

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

    def phrase_rank(self, query, inv_ind, N, doc_size):

        term_inverted_indexes = {}
        documents_appearing_in = {}
        tf = {}
        df = 0
        document_scores = {}

        for term in query:
            term_inverted_indexes[term] = self.get_term_entry_from_inverted_index(inv_ind, term)
            documents_appearing_in[term] = self.extract_all_documents_term_appears_in(term_inverted_indexes[term])

        intersection_of_documents = sorted(reduce(set.intersection, map(set, documents_appearing_in.values())))

        for doc in intersection_of_documents:
            positional_index = []
            for term in query:
                positional_index.append(term_inverted_indexes[term][doc])

            cons_count = self.consecutive_occ(positional_index)
            if cons_count > 0:
                tf[doc] = cons_count
                df += 1

        for doc in intersection_of_documents:

            if doc in tf.keys():
                document_scores[doc] = self.compute_weight_phrase_document(doc, tf[doc], df, N, doc_size)

        sorted_document_scores = sorted(document_scores.items(), key=lambda x: x[1], reverse=True)
        sorted_document_scores = sorted_document_scores[:100]
        return sorted_document_scores

if __name__ == '__main__':
    preprocessor = Preprocessing()
    bm25_model = bm25_model()
    phrase_bool = False

    with open('inverted_index.json') as results:
        with open('content_length.json') as docs:
            inv_ind = json.load(results)
            doc_size = json.load(docs)

    query = input("Enter query: ")
    if '"' in query:
        phrase_bool = True

    query = re.sub(r'[^\w]', ' ', query)
    query = preprocessor.preprocess_query(query)
    del query[0]
    del query[-1]

    if phrase_bool:
        phrase_query_results_dict = {}
        N = len(doc_size.keys())
        phrase_query_results_dict = bm25_model.phrase_rank(query, inv_ind, N, doc_size)
        print(phrase_query_results_dict)

    else:
        query_results_dict = {}
        N = len(doc_size.keys())
        query_results_dict = bm25_model.rank(query, inv_ind, N, doc_size)
        print(query_results_dict)
