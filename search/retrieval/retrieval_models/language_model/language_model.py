import json
import math
from functools import reduce
import datetime
from retrieval.retrieval_helpers.preprocessing import Preprocessing
from retrieval.retrieval_helpers.helpers import extract_all_documents_term_appears_in
from retrieval.retrieval_helpers.helpers import sort_document_scores
from retrieval.retrieval_helpers.helpers import consecutive_occ
from retrieval.retrieval_helpers.helpers import split_list


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
            if type(mini_index[term][1][document]) is list:
                tf = len(mini_index[term][1][document])
            else:
                tf = mini_index[term][1][document]
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

    def retrieval(self, query, inv_ind, N, doc_size, l_tot, date_ind, date_bool, use_pitman_yor_process=True,
                  boolean_docs=None):

        query_updated = []

        for i, t in enumerate(query):
            if len(query[i]) > 0:
                query_updated.append(query[i])

        singles = []
        phrases = []
        t_docs = []
        p_docs = []
        for term in query_updated:
            if len(term) == 1:
                singles.append(term[0])
            else:
                phrases.append(term)
        tot_docs = {}

        start_time = datetime.datetime.now()
        if singles:
            t_docs = self.rank(singles, inv_ind, N, doc_size, l_tot, date_ind, date_bool, use_pitman_yor_process, boolean_docs)
            if boolean_docs:
                boolean_ranked_articles = t_docs  # if using boolean, rank function returns the ranked articles
                return boolean_ranked_articles
        if phrases:
            p_docs = self.phrase_rank(phrases, inv_ind, N, doc_size, l_tot, date_ind, date_bool, boolean_docs)
            if boolean_docs:
                boolean_ranked_articles = p_docs
                return boolean_ranked_articles  # just as abo e

        print(f"Ranking with the lm model took {datetime.datetime.now() - start_time}")
        if t_docs and p_docs:
            tot_keys = set(list(t_docs.keys()) + list(p_docs.keys()))
            for k in tot_keys:
                tot_docs[k] = t_docs.get(k, 0) + p_docs.get(k, 0)
        elif t_docs:
            tot_docs = t_docs
        elif p_docs:
            tot_docs = p_docs

        sorted_articles = sort_document_scores(tot_docs, query)
        return sorted_articles

    def phrase_rank(self, query, mini_index, N, doc_sizes, length_collection, date_ind, date_bool, boolean_docs=None):

        document_scores = {}
        for phrase in query:
            documents_appearing_in = {}
            tf = {}
            df = 0
            for term in phrase:
                documents_appearing_in[term] = extract_all_documents_term_appears_in(mini_index[term][1])

            if date_bool:
                intersection_of_documents = list(set(
                    reduce(set.intersection, map(set, documents_appearing_in.values()))).intersection(date_ind))

            else:
                intersection_of_documents = list(reduce(set.intersection, map(set, documents_appearing_in.values())))

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
            if boolean_docs:
                if date_bool:
                    boolean_docs = set(boolean_docs).intersection(date_ind)
                doc_scores = self.compute_document_scores_phrase(boolean_docs, tf, df, N, doc_sizes, length_collection)
                ranked_articles = sort_document_scores(doc_scores, query)
                return ranked_articles
            document_scores = self.compute_document_scores_phrase(intersection_of_documents, tf, df, N, doc_sizes, length_collection)
        return document_scores

    def rank(self, query, mini_index, N, doc_sizes, l_tot, date_ind, date_bool, use_pitman_yor_process,
             boolean_docs=None):

        documents_appearing_in = {}
        query_term_frequency = {}
        union_of_documents = []
        union_bool = False
        intersection0 = []
        intersection1 = []
        intersection2 = []

        for term in query:
            if term in mini_index.keys():
                documents_appearing_in[term] = extract_all_documents_term_appears_in(mini_index[term][1])
                query_term_frequency[term] = query.count(
                    term)  # doing this here so we do not repeat it for each document

        if documents_appearing_in:
            if date_bool:
                print("doing date stuff")
                if boolean_docs:
                    boolean_docs = set(boolean_docs).intersection(date_ind)
                    ranked_articles = self.boolean_retrieval(boolean_docs,query, mini_index, use_pitman_yor_process, query_term_frequency, l_tot, doc_sizes)
                    return ranked_articles
                if len(list(documents_appearing_in.keys())) > 1:
                    intersection0 = list(set(
                        list(reduce(set.intersection, map(set, documents_appearing_in.values()))).intersection(
                            date_ind)))
                    if len(intersection0) < 100:
                        print("intersecting")
                        d1, d2 = split_list(list(documents_appearing_in.values()))
                        intersection1 = list(set(reduce(set.intersection, map(set, d1))).intersection(date_ind))
                        intersection2 = list(set(reduce(set.intersection, map(set, d2))).intersection(date_ind))
                        if len(set(intersection1 + intersection2)) < 100:
                            union_bool = True
                            union_of_documents = list(set(
                                reduce(set.union, map(set, documents_appearing_in.values()))).intersection(date_ind))
                        print("finished intersecting")
                else:
                    print("intersecting 2")
                    union_bool = True
                    union_of_documents = list(
                        set(reduce(set.union, map(set, documents_appearing_in.values()))).intersection(
                            date_ind))
                    print("finished intersecting 2")

            else:
                if boolean_docs:
                    ranked_articles = self.boolean_retrieval(boolean_docs, query, mini_index, use_pitman_yor_process, query_term_frequency, l_tot, doc_sizes)
                    return ranked_articles
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

        length_collection = l_tot  # length of the collection in terms
        # g = self.g  # discounting parameter - as used in paper "Improvements to BM25 and Language Model examined - used for pyp implementation
        length_query = len(query)  # length of the query
        document_scores = {}

        if not union_bool:
            total_inter = list(set(intersection0 + intersection1 + intersection2))

            document_scores = self.compute_document_scores(total_inter, query, mini_index,use_pitman_yor_process, query_term_frequency,
                                                           length_collection, length_query, doc_sizes)
            ## TO DO - Here find score with exactly equal values - or within 10% range - should be duplicates so only keep one
        else:

            if not union_of_documents:
                return False

            document_scores = self.compute_document_scores(union_of_documents, query, mini_index, use_pitman_yor_process, query_term_frequency,
                                                           length_collection, length_query, doc_sizes)

        return document_scores

    def compute_document_scores(self, document_list, query, mini_index, use_pitman_yor_process, query_term_frequency,
                                length_collection,
                                length_query, doc_sizes):
        document_scores = {}
        for document in document_list:
            score = 0
            for term in query:
                if term in mini_index.keys():
                    if use_pitman_yor_process:
                        w_t_d = self.compute_weight_term_document_pyp(query_term_frequency[term], term, mini_index,
                                                                      document, length_collection)
                        score += w_t_d
                    else:  # use lm-dirichlet smoothing
                        self.miu = 1089  # Different value identified in the paper compared to those used when
                        # pitman_yor_process is used
                        w_t_d = self.compute_weight_term_document(query_term_frequency[term], term, mini_index,
                                                                  document,
                                                                  length_collection)
                        score += w_t_d
            L_d = doc_sizes[str(document)]
            if use_pitman_yor_process:
                dicsounted_l_d = max((L_d - self.g * (L_d ** self.g)), 0)
                final_score = length_query * math.log(1 - (dicsounted_l_d / (L_d + self.miu))) + score
            else:
                final_score = length_query * math.log(self.miu / (L_d + self.miu)) + score
            document_scores[document] = final_score
        return document_scores

    def compute_document_scores_phrase(self, document_list, tf_dict, df, N, doc_sizes, length_collection):
        document_scores = {}
        for doc in document_list:

            if doc in tf_dict.keys():
                if doc in document_scores.keys():
                    document_scores[doc] += self.compute_weight_phrase_document(doc, tf_dict[doc], df, N, doc_sizes,
                                                                                length_collection)
                else:
                    document_scores[doc] = self.compute_weight_phrase_document(doc, tf_dict[doc], df, N, doc_sizes,
                                                                               length_collection)
        return document_scores

    def boolean_retrieval(self, boolean_docs, query, mini_index, use_pitman_yor_process, query_term_frequency, l_tot,
                          doc_sizes):
        document_scores = self.compute_document_scores(boolean_docs, query, mini_index,
                                                       use_pitman_yor_process,
                                                       query_term_frequency, l_tot, len(query), doc_sizes)
        ranked_articles = sort_document_scores(document_scores, query)
        return ranked_articles

if __name__ == '__main__':
    preprocessor = Preprocessing()
    Lanaguage_model = Language_model()

    with open('inverted_index.json') as results:
        with open('content_length.json') as docs:
            inv_ind = json.load(results)
            doc_size = json.load(docs)
