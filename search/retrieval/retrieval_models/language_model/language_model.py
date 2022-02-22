import json
import math
from functools import reduce

from retrieval.retrieval_helpers.preprocessing import Preprocessing
from retrieval.retrieval_helpers.helpers import extract_all_documents_term_appears_in


class Language_model:

    def __init__(self, miu):
        self.miu = miu # tuning parameter

    def compute_weight_term_document(self, tf_q, term, mini_index, document, length_collection):

        L_c = length_collection
        if document not in mini_index[term][1].keys():
            w_t_d = 0
        else:
            tf = len(mini_index[term][1][document])  # number of times term appears in document

            cf = mini_index[term][0] #  number of times the term occurs in the collection
            w_t_d = tf_q * math.log((tf / self.miu) * (L_c / cf) + 1)

        return w_t_d

    def compute_weight_term_document_pyp(self, tf_q, term, mini_index, document, length_collection, g):
        """
        Function to calculate term weight using the discounting terms introduced by the pitman-yor process
        """
        L_c = length_collection


        if document not in mini_index[term][1].keys():
            w_t_d = 0
        else:
            tf = len(mini_index[term][1][document])
            cf = mini_index[term][0]

            discounted_tf = max((tf - g*(tf**g)), 0)

            w_t_d = tf_q* math.log((discounted_tf* L_c)/(self.miu * cf) + 1)

        return w_t_d


    def retrieval(self, query, mini_index, N, doc_sizes, l_tot, use_pitman_yor_process):
        print("Using language model")
        documents_appearing_in = {}
        query_term_frequency = {}
        for term in query:
            documents_appearing_in[term] = extract_all_documents_term_appears_in(mini_index[term][1])
            query_term_frequency[term] = query.count(term)  # doing this here so we do not repeat it for each document

        union_of_documents = sorted(reduce(set.union, map(set, documents_appearing_in.values())))
        length_collection = l_tot  # length of the collection in terms
        g = 0.2 # discounting parameter - as used in paper "Improvements to BM25 and Language Model examined - used for pyp implementation
        length_query = len(query)  # length of the query
        document_scores = {}
        for document in union_of_documents:
            score = 0
            for term in query:
                    if use_pitman_yor_process:
                        w_t_d = self.compute_weight_term_document_pyp(query_term_frequency[term], term, mini_index, document, length_collection, g)
                        score += w_t_d
                    else:  # use lm-dirichlet smoothing
                        w_t_d = self.compute_weight_term_document(query_term_frequency[term], term, mini_index, document, length_collection)
                        score += w_t_d
            L_d = doc_sizes[str(document)]
            if use_pitman_yor_process:
                dicsounted_l_d = max((L_d - g*(L_d**g)), 0)
                final_score = length_query * math.log(1 - (dicsounted_l_d /( L_d + self.miu))) + score
            else:
                final_score = length_query * math.log(self.miu / (L_d + self.miu)) + score
            document_scores[document] = final_score

        sorted_document_scores = sorted(document_scores.items(), key=lambda x: x[1], reverse=True)
        sorted_document_ids = [id_score[0] for id_score in sorted_document_scores[:100]]
        for i, id in enumerate(sorted_document_ids[:20]):
            print("%d : %d" % (i+1, id))  # Printing rank:id (easier to see and compare in the terminal)
        return sorted_document_ids


if __name__ == '__main__':
    preprocessor = Preprocessing()
    Lanaguage_model = Language_model()

    with open('inverted_index.json') as results:
        with open('content_length.json') as docs:
            inv_ind = json.load(results)
            doc_size = json.load(docs)

