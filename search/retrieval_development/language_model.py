import json
import math
from functools import reduce

from search.retrieval_development.functions import get_term_entry_from_inverted_index, \
    extract_all_documents_term_appears_in, read_index_from_file
from search.retrieval_development.preprocessing import Preprocessing


class Language_model:

    def __init__(self, miu):
        self.miu = miu # tuning parameter

    def compute_weight_term_query(self, query, term, inv_index, document, length_collection):
        tf_q = query.count(term) # No of times term appears in query
        if document not in inv_index[term]:
            term_weight = 0
        else:
            cf = len(inv_index[term])  # number of times the term occurs in the collection
            tftd = len(inv_index[term][document])  # No of times term appears in current document
            term_weight = tf_q * math.log10((tftd/self.miu) * (length_collection/cf) + 1)
        return term_weight




    def retrieval(self, query, inv_index, N, doc_sizes):
        """
        Function to implement language model based retrieval using dirichlet smoothing
        """

        term_inverted_indexes = {}
        documents_appearing_in = {}
        for term in query:
            term_inverted_indexes[term] = get_term_entry_from_inverted_index(inv_index, term)
            documents_appearing_in[term] = extract_all_documents_term_appears_in(term_inverted_indexes[term])
        union_of_documents = sorted(reduce(set.union, map(set, documents_appearing_in.values())))

        document_scores = {}
        L_q = len(query) # Lq parameter = length of query
        L_c = len(inv_index) # total length of the collection in terms
        for document in union_of_documents:
            doc_size_value = int(doc_sizes[document] if doc_sizes[document] != 'NaN' else 1)
            score = 0
            for term in query:
                term_weight = self.compute_weight_term_query(query, term, inv_index, document, L_c)
                score += term_weight

            score = L_q * math.log10(self.miu / doc_size_value) + score

            document_scores[document] = score
        sorted_document_scores = sorted(document_scores.items(), key=lambda x: x[1], reverse=True)
        sorted_document_scores = sorted_document_scores[:100]
        return sorted_document_scores


if __name__ == '__main__':
    preprocessor = Preprocessing()
    lm = Language_model(miu=3)

#    inverted_index = read_index_from_file("inverted_index.txt")

    with open('inverted_index.json') as results:
        with open('content_length.json') as docs:
            inv_ind = json.load(results)
            doc_sizes = json.load(docs)
            query = input("Enter query: ")
            query = preprocessor.preprocess_query(query)
            query_results_dict = {}
            N = len(doc_sizes.keys())
            query_results_dict = lm.retrieval(query, inv_ind, N, doc_sizes)
            stop = 0

