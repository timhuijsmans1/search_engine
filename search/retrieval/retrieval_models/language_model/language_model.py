import json
import math
from functools import reduce

from retrieval.retrieval_helpers.preprocessing import Preprocessing
from retrieval.retrieval_helpers.helpers import extract_all_documents_term_appears_in
from retrieval.retrieval_helpers.helpers import sort_document_scores
from retrieval.retrieval_helpers.helpers import consecutive_occ


class Language_model:

    def __init__(self, miu, g):
        self.miu = miu  # Tuning Parameter
        self.g = g  # Tuning Parameter

    def compute_weight_term_document(self, tf_q, term, mini_index, document, length_collection):

        L_c = length_collection
        if document not in mini_index[term][1].keys():
            w_t_d = 0
        else:
            tf = len(mini_index[term][1][document])  # number of times term appears in document

            cf = mini_index[term][0]  # number of times the term occurs in the collection
            w_t_d = tf_q * math.log((tf / self.miu) * (L_c / cf) + 1)

        return w_t_d

    def compute_weight_term_document_pyp(self, tf_q, term, mini_index, document, length_collection):
        """
        Function to calculate term weight using the discounting terms introduced by the pitman-yor process
        g = Parameter for the pyp process smoothing function - currently set as the one seen in the paper
        """
        L_c = length_collection
        g = self.g
        if document not in mini_index[term][1].keys():
            w_t_d = 0
        else:
            tf = len(mini_index[term][1][document])
            cf = mini_index[term][0]

            discounted_tf = max((tf - g * (tf ** g)), 0)

            w_t_d = tf_q * math.log((discounted_tf * L_c) / (self.miu * cf) + 1)

        return w_t_d

    def compute_weight_phrase_document(self, document, tf, df, N, doc_sizes, length_collection):
        """
        Using the same formula as the LM with Dirichet smoothing, but treating the phrase as one term with values
        computed in the phrase_retrieval function
        tf - term frequency in the current document
        df - total collection frequency
        """
        L_c = length_collection
        cf = df
        w_p_d = math.log((tf / self.miu) * (L_c / cf) + 1)
        return w_p_d

    def retrieval(self, query, inv_ind, N, doc_size, l_tot, use_pitman_yor_process):

        singles = []
        phrases = []
        t_docs = []
        p_docs = []
        for term in query:
            if len(term) == 1:
                singles.append(term[0])
            else:
                phrases.append(term)
        tot_docs = {}
        if singles:
            t_docs = self.rank(singles, inv_ind, N, doc_size, l_tot, use_pitman_yor_process)
        if phrases:
            p_docs = self.phrase_rank(phrases, inv_ind, N, doc_size, l_tot)

        if t_docs and p_docs:
            tot_keys = set(list(t_docs.keys()) + list(p_docs.keys()))
            for k in tot_keys:
                tot_docs[k] = t_docs.get(k, 0) + p_docs.get(k, 0)
        elif t_docs:
            tot_docs = t_docs
        elif p_docs:
            tot_docs = p_docs

        sorted_docs = sort_document_scores(tot_docs)
        return sorted_docs

    def phrase_rank(self, query, mini_index, N, doc_sizes, length_collection):

        document_scores = {}
        for phrase in query:
            documents_appearing_in = {}
            phrase = set(phrase)
            tf = {}
            df = 0
            for term in phrase:
                documents_appearing_in[term] = extract_all_documents_term_appears_in(mini_index[term][1])

            intersection_of_documents = sorted(reduce(set.intersection, map(set, documents_appearing_in.values())))
            for doc in intersection_of_documents:
                positional_index = []
                for term in phrase:
                    positional_index.append(mini_index[term][1][doc])  # term positions in the document


                cons_count = consecutive_occ(positional_index)
                if cons_count > 0:
                    tf[doc] = cons_count
                    df += 1  # total document frequency of the given phrase
            if not intersection_of_documents:
                return False

            for doc in intersection_of_documents:

                if doc in tf.keys():
                    if doc in document_scores.keys():
                        document_scores[doc] += self.compute_weight_phrase_document(doc, tf[doc], df, N, doc_sizes,
                                                                               length_collection)
                    else:
                        document_scores[doc] = self.compute_weight_phrase_document(doc, tf[doc], df, N, doc_sizes,
                                                                                    length_collection)

        return document_scores

    def rank(self, query, mini_index, N, doc_sizes, l_tot, use_pitman_yor_process):
        documents_appearing_in = {}
        query_term_frequency = {}
        union_of_documents = []

        for term in query:
            if term in mini_index.keys():
                documents_appearing_in[term] = extract_all_documents_term_appears_in(mini_index[term][1])
                query_term_frequency[term] = query.count(term)  # doing this here so we do not repeat it for each document

        if documents_appearing_in:
            union_of_documents = sorted(reduce(set.union, map(set, documents_appearing_in.values())))
        length_collection = l_tot  # length of the collection in terms
        # g = self.g  # discounting parameter - as used in paper "Improvements to BM25 and Language Model examined - used for pyp implementation
        length_query = len(query)  # length of the query
        sorted_scores = self.assign_scores(union_of_documents, query, mini_index, use_pitman_yor_process, query_term_frequency, length_collection, doc_sizes, abbv_bool)
        return sorted_scores


    # def assign_scores(self, union_of_documents, query, mini_index, use_pitman_yor_process, query_term_frequency, length_collection, doc_sizes, abbv_bool):
    #     document_scores = {}
    #     length_query = len(query)
    #     for document in union_of_documents:
    #         score = 0
    #         for term in query:
    #             if term in mini_index.keys():
    #                 if use_pitman_yor_process:
    #                     w_t_d = self.compute_weight_term_document_pyp(query_term_frequency[term], term, mini_index,
    #                                                                   document, length_collection)
    #                     score += w_t_d
    #                 else:  # use lm-dirichlet smoothing
    #                     self.miu = 1089  # Different value identified in the paper compared to those used when
    #                     # pitman_yor_process is used
    #                     w_t_d = self.compute_weight_term_document(query_term_frequency[term], term, mini_index, document,
    #                                                               length_collection)
    #                     score += w_t_d
    #         L_d = doc_sizes[str(document)]
    #         if use_pitman_yor_process:
    #             dicsounted_l_d = max((L_d - self.g * (L_d ** self.g)), 0)
    #             final_score = length_query * math.log(1 - (dicsounted_l_d / (L_d + self.miu))) + score
    #         else:
    #             final_score = length_query * math.log(self.miu / (L_d + self.miu)) + score
    #         document_scores[document] = final_score
    #     ## TO DO - Here find score with exactly equal values - or within 10% range - should be duplicates so only keep one
    #
    #     return document_scores


if __name__ == '__main__':
    preprocessor = Preprocessing()
    Lanaguage_model = Language_model()

    with open('inverted_index.json') as results:
        with open('content_length.json') as docs:
            inv_ind = json.load(results)
            doc_size = json.load(docs)
