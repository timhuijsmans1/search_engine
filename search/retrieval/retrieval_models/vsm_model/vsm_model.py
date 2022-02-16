import json
import math
from functools import reduce
import xml.etree.ElementTree as ET
import numpy as np

### Import working locally on Vlad's machine
# from search.retrieval.retrieval_helpers.helpers import extract_all_documents_term_appears_in
# from search.retrieval.retrieval_helpers.preprocessing import Preprocessing

###
from retrieval.retrieval_helpers.helpers import extract_all_documents_term_appears_in
from retrieval.retrieval_helpers.preprocessing import Preprocessing


class Vsm_model:

    def compute_weight_term_document(self, term, document, positional_inverted_index, documents_appearing_in, N,
                                     doc_size):
        """
        Function to compute the term weight based on TFIDF term weighing
        """

        if document not in positional_inverted_index[term][1]:
            w_t_d = 0
        else:

            doc_size_value = int(doc_size[str(document)]) if doc_size[
                                                                 str(document)] != 'NaN' else 1  # Extracting doc size -
            # some elements have 'NaN' entry TO DO: ask Humzah to check -
            tf = len(positional_inverted_index[term][1][document]) # if we divide by the doc size then value gets really low
            # which then affects the logarithms and all w_t_d terms become 0 When we were normalizing before it was
            # using an implementation without the log  / doc_size[str(document)]  # how often the term appears in the
            # current document /document size (for normalization)

            tf = 1 + math.log10(tf)
            df = len(documents_appearing_in[term])
            idf = math.log10((N - df) / df)  # Total Number of Docs / Numbers of docs with the term in them
            w_t_d = tf * idf  # using lecture slides
            if w_t_d < 0:
                w_t_d = 0
        return w_t_d

    def compute_weight_term_query(self, term, query, N, documents_appearing_in):
        """
        Slide 21 - lecture 7 - red boxes are for query
        follows lnc.ltc schema -
        """
        tf = 1 + math.log10(
            query.count(term))  # how many times the term appears in the query / query_length (for normalization)
        df = len(documents_appearing_in[term])
        idf = math.log10(N / df)  # IDF is the same regardless if we are looking for query or document weight term
        w_t_q = tf * idf
        return w_t_q

    def ranked_retrieval(self, query, mini_index, N, doc_sizes):
        """
        Ranked retrieval using cosine similarity algorithm
        N - total number of documents in the collection
        """

        term_inverted_indexes = {}  # Dictionary to store the entries in the inverted index of each term in the query
        documents_appearing_in = {}  # Dictionary to store the documents each term in the query appears in
        for term in query:
            documents_appearing_in[term] = extract_all_documents_term_appears_in(mini_index[term][1])

        # Find the union of docs between all terms in the query
        union_of_documents = sorted(reduce(set.union, map(set, documents_appearing_in.values())))

        document_scores = {}  # Dictionary to map document id with computed score
        for document in union_of_documents:
            score = 0
            document_vector = []
            query_vector = []
            for term in query:
                w_t_d = self.compute_weight_term_document(term, document, mini_index, documents_appearing_in, N,
                                                          doc_sizes)
                w_t_q = self.compute_weight_term_query(term, query, N, documents_appearing_in)
                document_vector.append(w_t_d)
                query_vector.append(w_t_q)
                print("score before multiplication: ", score)
                print("weight term document: ", w_t_d)
                print("weight term query: ", w_t_q)
                score += w_t_d * w_t_q  # dot product (the summation of the terms in each vector multiplied)
                print("score after multiplication: ", score)
            print("score is: %f times %f = %f", w_t_d, w_t_q, score)
            document_vector_magnitude = np.linalg.norm(document_vector)
            query_vector_magnitude = np.linalg.norm(query_vector)
            print("Doc vector magnitude")
            print(document_vector_magnitude)
            print("query vector magnitude")
            print(query_vector_magnitude)
            print()
            score = score / (
                    document_vector_magnitude * query_vector_magnitude)  # the product of the magnitudes of the two vectors
            score = float(score)

            document_scores[document] = score  # append the final score for each document
        sorted_document_scores = sorted(document_scores.items(), key=lambda x: x[1], reverse=True)
        print("Sorted doc score")
        print(sorted_document_scores)
        sorted_document_scores = [doc_and_score[0] for doc_and_score in sorted_document_scores[:20]]
        return sorted_document_scores


if __name__ == '__main__':
    preprocessor = Preprocessing()
    Vsm_model = Vsm_model()  # Initialise class
    # Read the collection
    # tree = ET.parse("trec.5000.xml")
    # document_dic = create_doc_dictionary(tree, preprocessor)
    # inverted_index = read_index_from_file("inverted_index.txt")
    # queries = ["income tax reduction", "peace in the Middle East", "unemployment rate in UK",
    #            "industry in Scotland", "the industries of computers", "Microsoft Wdinows", "stock market in Japan",
    #            "the education with computers", "health industry", "campaigns of political parties"]
    #

    with open('inverted_index.json') as results:
        with open('content_length.json') as docs:
            inv_ind = json.load(results)
            doc_size = json.load(docs)
            query = input("Enter query: ")
            query = preprocessor.preprocess_query(query)
            query_results_dict = {}
            N = len(doc_size.keys())
            query_results_dict = Vsm_model.ranked_retrieval(query, inv_ind, N, doc_size)
            stop = 0
