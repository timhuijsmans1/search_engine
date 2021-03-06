import math
from functools import reduce
import re
import xml.etree.ElementTree as ET
import numpy as np
import json
from collections import defaultdict, OrderedDict
import time
import datetime
from retrieval.retrieval_helpers.preprocessing import Preprocessing
from retrieval.retrieval_helpers.helpers import sort_document_scores
from retrieval.retrieval_helpers.helpers import consecutive_occ
from retrieval.retrieval_helpers.helpers import split_list
from retrieval.retrieval_helpers.helpers import seperate_mix


class Bm25_model:

    def compute_weight_term_document(self, term, document, positional_inverted_index, documents_appearing_in, N,
                                     doc_size, len_tot, l_a, idf):

        l_tot = len_tot
        l_avg = l_a
        k = 1.5

        if term in positional_inverted_index.keys():
            if document not in positional_inverted_index[term][1].keys():

                w_t_d = 0
            else:
                if type(positional_inverted_index[term][1][document]) is list:
                    tf = len(positional_inverted_index[term][1][document])
                else:
                    tf = positional_inverted_index[term][1][document]

                d = doc_size[str(document)] / l_avg
                w_t_d = idf * (tf / ((k * d) + tf + 0.5))

        else:
            w_t_d = 0

        return w_t_d

    def compute_weight_phrase_document(self, document, tf, df, N,
                                       doc_size, len_tot):
        l_tot = len_tot
        l_avg = 0
        k = 1.5

        l_avg = l_tot / N
        idf = math.log(1 + ((N - df + 0.5) / (df + 0.5)))
        d = doc_size[str(document)] / l_avg
        w_t_d = idf * (tf / ((k * d) + tf + 0.5))

        return w_t_d

    def get_term_entry_from_inverted_index(self, inverted_index, term):

        if term in inverted_index.keys():
            inverted_index_term = inverted_index[term]
            return inverted_index_term

    def extract_documents_term_appears_in(self, inverted_index_term):

        documents_term_appears_in = []
        if inverted_index_term:
            for k in inverted_index_term.keys():
                documents_term_appears_in.append(k)
        return documents_term_appears_in

    # def abbv(self, query, abbv_query, inv_ind, N, doc_size, l_tot):
    #
    #     term_inverted_indexes = {}
    #     documents_appearing_in = {}
    #     query = set(query)
    #     l_avg = l_tot / N
    #     tf = {}
    #     df_p = 0
    #     union_of_documents = []
    #     document_scores = {}
    #
    #     for term in query:
    #         term_inverted_indexes[term] = self.get_term_entry_from_inverted_index(inv_ind, term)
    #         if term_inverted_indexes[term]:
    #             documents_appearing_in[term] = self.extract_documents_term_appears_in(term_inverted_indexes[term][1])
    #             df = len(documents_appearing_in[term])
    #             idf = math.log(1 + ((N - df + 0.5) / (df + 0.5)))
    #             union_of_documents = sorted(reduce(set.union, map(set, documents_appearing_in.values())))
    #
    #
    #     for term in abbv_query:
    #         term_inverted_indexes[term] = self.get_term_entry_from_inverted_index(inv_ind, term)
    #         documents_appearing_in[term] = self.extract_documents_term_appears_in(term_inverted_indexes[term][1])
    #
    #     intersection_of_documents = sorted(reduce(set.intersection, map(set, documents_appearing_in.values())))
    #
    #     if union_of_documents:
    #         for document in union_of_documents:
    #
    #             score = 0
    #             document_vector = []
    #
    #             for term in query:
    #                 w_t_d = self.compute_weight_term_document(term, document, inv_ind, documents_appearing_in, N, doc_size, l_tot, l_avg, idf)
    #                 document_vector.append(w_t_d)
    #                 score += w_t_d
    #
    #             document_scores[document] = score
    #
    #     for doc in intersection_of_documents:
    #         positional_index = []
    #         for term in abbv_query:
    #             positional_index.append(term_inverted_indexes[term][1][doc])
    #
    #         cons_count = self.consecutive_occ(positional_index)
    #         if cons_count > 0:
    #             tf[doc] = cons_count
    #             df_p += 1
    #
    #     if not intersection_of_documents:
    #         return False
    #
    #     for doc in intersection_of_documents:
    #
    #         if doc in list(tf.keys()):
    #             if doc in document_scores.keys():
    #                 document_scores[doc] += self.compute_weight_phrase_document(doc, tf[doc], df_p, N, doc_size, l_tot)
    #             else:
    #                 document_scores[doc] = self.compute_weight_phrase_document(doc, tf[doc], df_p, N, doc_size, l_tot)
    #
    #     sorted_document_scores = sorted(document_scores.items(), key=lambda x: x[1], reverse=True)
    #     sorted_document_scores = [i[0] for i in sorted_document_scores[:100]]
    #
    #     return sorted_document_scores

    # def abbv(self, query, abbv_query, inv_ind, N, doc_size, l_tot, abbv_bool):
    #
    #     tot_docs = {}
    #     t_docs = self.rank(query, inv_ind, N, doc_size, l_tot, abbv_bool)
    #     p_docs = self.phrase_rank(abbv_query, inv_ind, N, doc_size, l_tot, abbv_bool)
    #
    #     if t_docs and p_docs:
    #         tot_keys = set(list(t_docs.keys()) + list(p_docs.keys()))
    #         for k in tot_keys:
    #             tot_docs[k] = t_docs.get(k, 0) + p_docs.get(k, 0)
    #     elif t_docs:
    #         tot_docs = t_docs
    #     elif p_docs:
    #         tot_docs = p_docs
    #
    #     sorted_docs = sort_document_scores(tot_docs)
    #     return sorted_docs

    def retrieval(self, query, inv_ind, N, doc_size, l_tot, date_ind, date_bool, boolean_docs=None):

        start = time.time()
        t_docs = []
        p_docs = []

        singles, phrases = seperate_mix(query)
        tot_docs = {}

        start_time = datetime.datetime.now()
        if singles:
            t_docs = self.rank(singles, inv_ind, N, doc_size, l_tot, date_ind, date_bool, boolean_docs)
            if boolean_docs:
                boolean_ranked_articles = t_docs  # in case of using boolean, the rank function returns the ranked articles and we do not want to go into sorting agian below
                return boolean_ranked_articles
        if phrases:
            p_docs = self.phrase_rank(phrases, inv_ind, N, doc_size, l_tot, date_ind, date_bool, boolean_docs)
            if boolean_docs:
                boolean_ranked_articles = p_docs
                return boolean_ranked_articles  # same as above, in the case of using phrase with boolean on the rank functions returns the ranked articles
        print(f"Ranking with the bm25 model took {datetime.datetime.now() - start_time}")

        if t_docs and p_docs:
            tot_keys = set(list(t_docs.keys()) + list(p_docs.keys()))
            for k in tot_keys:
                tot_docs[k] = t_docs.get(k, 0) + p_docs.get(k, 0)
        elif t_docs:
            tot_docs = t_docs
        elif p_docs:
            tot_docs = p_docs

        sorted_articles = sort_document_scores(tot_docs, query)
        end = time.time()
        print(end - start)
        return sorted_articles

    def rank(self, query, inv_ind, N, doc_size, l_tot, date_ind, date_bool, boolean_docs=None):

        term_inverted_indexes = {}
        documents_appearing_in = {}
        query = set(query)
        l_avg = l_tot / N
        union_of_documents = []
        union_bool = False
        intersection0 = []
        intersection1 = []
        intersection2 = []

        for term in query:
            term_inverted_indexes[term] = self.get_term_entry_from_inverted_index(inv_ind, term)
            if term_inverted_indexes[term]:
                documents_appearing_in[term] = self.extract_documents_term_appears_in(term_inverted_indexes[term][1])
                df = len(documents_appearing_in[term])
                idf = math.log(1 + ((N - df + 0.5) / (df + 0.5)))

        if documents_appearing_in:

            if date_bool:
                if boolean_docs:
                    boolean_docs = set(boolean_docs).intersection(date_ind)
                    ranked_articles = self.boolean_retrieval(boolean_docs, query, inv_ind, documents_appearing_in, N, doc_size, l_tot, l_avg,
                                                             idf)
                    return ranked_articles

                if len(list(documents_appearing_in.keys())) > 1:
                    intersection0 = list(
                        set(reduce(set.intersection, map(set, documents_appearing_in.values()))).intersection(date_ind))
                    if len(intersection0) < 100:
                        d1, d2 = split_list(list(documents_appearing_in.values()))
                        intersection1 = list(set(reduce(set.intersection, map(set, d1))).intersection(date_ind))
                        intersection2 = list(set(reduce(set.intersection, map(set, d2))).intersection(date_ind))
                        if len(set(intersection1 + intersection2)) < 100:
                            union_bool = True
                            union_of_documents = list(
                                set(reduce(set.union, map(set, documents_appearing_in.values()))).intersection(
                                    date_ind))
                else:
                    union_bool = True
                    union_of_documents = list(
                        set(reduce(set.union, map(set, documents_appearing_in.values()))).intersection(date_ind))

            else:
                if boolean_docs:
                    ranked_articles = self.boolean_retrieval(boolean_docs, query, inv_ind, documents_appearing_in, N, doc_size, l_tot,
                                                             l_avg, idf)
                    return ranked_articles  # boolean retrieval sorts and returns the articles so exit the function here

                if len(list(documents_appearing_in.keys())) > 1:
                    intersection0 = list(reduce(set.intersection, map(set, documents_appearing_in.values())))
                    if len(intersection0) < 100:
                        d1, d2 = split_list(list(documents_appearing_in.values()))
                        intersection1 = list(reduce(set.intersection, map(set, d1)))
                        intersection2 = list(reduce(set.intersection, map(set, d2)))
                        if len(set(intersection1 + intersection2)) < 100:
                            union_bool = True
                            union_of_documents = list(reduce(set.union, map(set, documents_appearing_in.values())))

                else:
                    union_bool = True
                    union_of_documents = list(reduce(set.union, map(set, documents_appearing_in.values())))

        if not union_bool:
            total_inter = list(set(intersection0 + intersection1 + intersection2))

            document_scores = self.compute_document_scores(total_inter, query, inv_ind, documents_appearing_in, N,
                                                           doc_size, l_tot, l_avg, idf)

        else:

            if not union_of_documents:
                return False

            document_scores = self.compute_document_scores(union_of_documents, query, inv_ind, documents_appearing_in,
                                                           N, doc_size, l_tot, l_avg, idf)

        return document_scores

        # else:
        #     sorted_scores = sort_document_scores(document_scores)
        #     return sorted_scores

    def compute_document_scores(self, documents_list, query, inv_ind, documents_appearing_in, N, doc_size, l_tot, l_avg,
                                idf):
        document_scores = {}
        for document in documents_list:
            score = 0
            document_vector = []
            for term in query:
                w_t_d = self.compute_weight_term_document(term, document, inv_ind, documents_appearing_in, N, doc_size,
                                                          l_tot, l_avg, idf)
                document_vector.append(w_t_d)
                score += w_t_d
            document_scores[document] = score
        return document_scores

    def boolean_retrieval(self, boolean_docs, query, mini_index, documents_appearing_in, N, doc_size, l_tot, l_avg, idf):
        document_scores = self.compute_document_scores(boolean_docs, query, mini_index, documents_appearing_in,
                                                           N, doc_size, l_tot, l_avg, idf)
        ranked_articles = sort_document_scores(document_scores, query)
        return ranked_articles

    def phrase_rank(self, query, inv_ind, N, doc_size, l_tot, date_ind, date_bool, boolean_docs=None):

        document_scores = {}
        for phrase in query:
            term_inverted_indexes = {}
            documents_appearing_in = {}
            tf = {}
            df = 0

            for term in phrase:
                term_inverted_indexes[term] = self.get_term_entry_from_inverted_index(inv_ind, term)
                if term_inverted_indexes[term]:
                    documents_appearing_in[term] = self.extract_documents_term_appears_in(
                        term_inverted_indexes[term][1])
            if date_bool:
                intersection_of_documents = list(
                    set(reduce(set.intersection, map(set, documents_appearing_in.values()))).intersection(date_ind))

            else:
                intersection_of_documents = list(reduce(set.intersection, map(set, documents_appearing_in.values())))

            for doc in intersection_of_documents:
                positional_index = []
                for term in phrase:
                    positional_index.append(term_inverted_indexes[term][1][doc])

                cons_count = consecutive_occ(positional_index)
                if cons_count > 0:
                    tf[doc] = cons_count
                    df += 1

            if not intersection_of_documents:
                return False
            if boolean_docs:
                if date_bool:
                    boolean_docs = set(boolean_docs).intersection(date_ind)
                doc_scores = self.compute_document_scores_phrase(boolean_docs, tf, df, N, doc_size, l_tot)
                ranked_articles = self.boolean_retrieval(doc_scores, query)
                return ranked_articles
            document_scores = self.compute_document_scores_phrase(document_scores, intersection_of_documents, tf, df, N, doc_size, l_tot)
        return document_scores


    def compute_document_scores_phrase(self, document_scores, documents_list, tf_dict, df, N, doc_size, l_tot):

        for doc in documents_list:
            if doc in tf_dict.keys():
                if doc in document_scores.keys():
                    document_scores[doc] += self.compute_weight_phrase_document(doc, tf_dict[doc], df, N, doc_size,
                                                                                l_tot)
                else:
                    document_scores[doc] = self.compute_weight_phrase_document(doc, tf_dict[doc], df, N, doc_size,
                                                                               l_tot)
        return document_scores
