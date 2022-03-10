import json
import numpy as np
import datetime
import sys
import pandas as pd
import csv

from retrieval.models import Article
from retrieval.retrieval_helpers.index_loader import load_mini_index
from retrieval.retrieval_helpers.preprocessing import Preprocessing
from retrieval.retrieval_helpers.helpers import write_results_to_file
from retrieval.retrieval_helpers.helpers import spellcheck_query
from retrieval.retrieval_helpers.helpers import is_proximity_query
from retrieval.retrieval_helpers.helpers import find_boolean_operators
from retrieval.retrieval_models.bm25_model.bm25_model import Bm25_model
from retrieval.retrieval_models.vsm_model.vsm_model import Vsm_model
from retrieval.retrieval_helpers.helpers import json_loader
from retrieval.retrieval_helpers.helpers import date2doc_initializer
from retrieval.retrieval_models.language_model.language_model import Language_model
from retrieval.retrieval_models.proximity_retrieval.proximity_retrieval import proximity_retrieval
from retrieval.retrieval_models.boolean_retrieval.boolean_retrieval import boolean_retrieval
from retrieval.retrieval_helpers.index_compression import *


class RetrievalExecution:

    # date2doc = date2doc_initializer(json_loader("retrieval/data/date2doc.json"))
    
    print("loading in search dictionaries")
    word2byte = json_loader("retrieval/data/word2byte.json")
    date2doc = date2doc_initializer(json_loader("retrieval/data/date2doc.json"))
    doc_sizes = json_loader("retrieval/data/doc_sizes.json")
    print("done loading all startup files")

    print("loading and compressing index")
    encoded_index = index_compressor('retrieval/data/final_index.json')
    print(f"finished encoding")

    print("sizes in memory:")
    print(f"1. date2doc: {total_size(date2doc) / 1000000} mb")
    print(f"1. doc_sizes: {total_size(doc_sizes) / 1000000} mb")
    print(f"1. word2byte: {total_size(word2byte) / 1000000} mb")
    print(f"1. encoded index: {total_size(encoded_index) / 1000000} mb")
    
    abv_dict = {}
    with open("retrieval/data/Fin_abbv.csv", 'r') as fin_abbv:
        abbv_temp = csv.reader(fin_abbv)
        for a, m in abbv_temp:
            abv_dict[a] = m

    def __init__(
            self,
            query,
            total_doc_number,
    ):

        preprocessing = Preprocessing()
        self.initial_query = query
        self.has_term_been_corrected = False
        self.corrected_query = ""

        self.N = total_doc_number
        self.abv_bool = False
        if '"' in query:
            self.phrase_bool = True
        else:
            self.phrase_bool = False

        for t in query.split():
            self.abv_dict_keys = [i.strip() for i in self.abv_dict.keys()]
            if t.upper() in self.abv_dict_keys:
                self.query_abv = self.abv_dict[t.upper()]
                self.abv_bool = True

        # if not self.abv_bool:
        #     query = spellcheck_query(query)

        self.proximity_query = False  # defining it before checking - if check fails have flag for checking before
        # retrieval
        self.boolean_search = False
        if is_proximity_query(query):
            self.proximity_query = True
            self.proximity_value, self.pre_processed_query = preprocessing.preprocess_proximity_query(query)
            return
            # only working with query in the format #15(term1, term2) for now # TO DO: Maybe handle error and raise
            # message to user? return
        bool_operators = find_boolean_operators(query)
        if len(bool_operators) > 0:
            self.boolean_search = True
            self.pre_processed_query, self.boolean_operators, self.positions_with_parentheses = preprocessing.preprocess_boolean_query(query,
                                                                                                      bool_operators)
            return

        query, self.has_term_been_corrected = spellcheck_query(
                query, self.abv_bool)  # only spell check query if it's not boolean or proximity retrieval
        self.corrected_query = query  # save the spellchecked query before pre processing it

        # pre process query
        self.pre_processed_query = preprocessing.apply_preprocessing(query)

        # get the original, the abv and the combined query, to execute the index retrieval only once
        if self.abv_bool:
            self.pre_processed_abv_query = preprocessing.apply_preprocessing(self.query_abv)
            self.original_query = self.pre_processed_query
            self.pre_processed_query = self.pre_processed_query + self.pre_processed_abv_query

        return

    def mini_index_builder(self):

        start_time = datetime.datetime.now()

        print("")
        self.mini_index = load_mini_index(self.pre_processed_query, "retrieval/data/index.json", self.word2byte)
        print("the mini index contains the words:", self.mini_index.keys())

        print(f"building the mini index and decoding took {datetime.datetime.now() - start_time}")

        # check if mini_index is valid (at least one word of query is in the index)
        return self.valid_index()

    def get_date_range_union(self, start_date, end_date):
        doc_numbers = set()

        # get all dates in the range provided as a list of datetime objects
        date_range = pd.date_range(start_date, end_date).tolist()

        for date in date_range:
            date_docs_set = self.date2doc.get(date, set())
            doc_number = doc_numbers | date_docs_set

        return doc_numbers

    def database_retrieval(self, doc_numbers):
        return {doc_no: Article.objects.get(document_id=doc_no) for doc_no in doc_numbers}

    def valid_index(self):
        """
        If the index does not return any documents,
        we can instantly return a page saying there
        are no results for the input query.
        """
        if len(self.mini_index.keys()) == 0:
            return False
        else:
            return True

    def bm25_ranking(self):

        bm25 = Bm25_model()

        print(self.abv_bool)

        self.l_tot = sum(list(self.doc_sizes.values()))

        if self.phrase_bool:
            ranked_docs = bm25.phrase_rank(self.pre_processed_query, self.mini_index, self.N, self.doc_sizes,
                                           self.l_tot)
        elif self.abv_bool:
            ranked_docs = bm25.abbv(self.original_query, self.pre_processed_abv_query, self.mini_index, self.N,
                                    self.doc_sizes, self.l_tot)
        else:
            ranked_docs = bm25.rank(self.pre_processed_query, self.mini_index, self.N, self.doc_sizes, self.l_tot)

        return ranked_docs

    def vsm_ranking(self):
        vsm = Vsm_model()
        ranked_docs = vsm.ranked_retrieval(self.pre_processed_query, self.mini_index, self.N, self.doc_sizes)
        return ranked_docs

    def lm_ranking(self):
        lm = Language_model(miu=1303, g=0.2)
        l_tot = sum(list(self.doc_sizes.values()))

        if self.phrase_bool:
            ranked_docs = lm.phrase_retrieval(self.pre_processed_query, self.mini_index, self.N, self.doc_sizes, l_tot)
        else:
            ranked_docs = lm.retrieval(self.pre_processed_query, self.mini_index, self.N, self.doc_sizes, l_tot,
                                       use_pitman_yor_process=True)
        return ranked_docs

    def execute_ranking(self, used_model, start_date, end_date):
        # returns false if none of the query terms match the index
        if self.mini_index_builder() == False:
            return False

        else:
            # if date filters are provided, get the date range doc union
            if start_date and end_date:
                docs_in_date_range = self.get_date_range_union(start_date, end_date)

            # document ranking
            start_time = datetime.datetime.now()

            if self.proximity_query:  # if we are doing a proximtiy query no need to check which model is used,
                # just retrieve the docs
                ranked_doc_numbers = proximity_retrieval(self.mini_index, self.proximity_value)
                ranked_article_objects = self.database_retrieval(ranked_doc_numbers)
                print(f"database retrieval took {datetime.datetime.now() - start_time}")
                return ranked_article_objects, self.has_term_been_corrected, self.corrected_query, self.initial_query
            elif self.boolean_search:
                ranked_doc_numbers = boolean_retrieval(self.boolean_operators, self.mini_index, self.N, self.positions_with_parentheses)
                ranked_article_objects = self.database_retrieval(ranked_doc_numbers)
                print(f"database retrieval took {datetime.datetime.now() - start_time}")
                return ranked_article_objects, self.has_term_been_corrected, self.corrected_query, self.initial_query

            if used_model == "bm25":
                ranked_doc_numbers = self.bm25_ranking()

            if used_model == "vsm":
                ranked_doc_numbers = self.vsm_ranking()

            if used_model == "lm":
                ranked_doc_numbers = self.lm_ranking()

            # write_results_to_file(ranked_doc_numbers, used_model, self.pre_processed_query)  # writing ids retrieved
            # to file
            start_time = datetime.datetime.now()
            # these can be re-ordered according to their date
            ranked_article_objects = self.database_retrieval(ranked_doc_numbers)
            print(f"database retrieval took {datetime.datetime.now() - start_time}")

            return ranked_article_objects, self.has_term_been_corrected, self.corrected_query, self.initial_query