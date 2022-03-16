import json
import ujson
import time

import numpy as np
import datetime
import sys
import pandas as pd
import csv
import re

from retrieval.retrieval_helpers.index_loader import load_mini_index
from retrieval.retrieval_helpers.preprocessing import Preprocessing
from retrieval.retrieval_helpers.helpers import write_results_to_file
from retrieval.retrieval_helpers.helpers import abv_loader
from retrieval.retrieval_helpers.helpers import spellcheck_query
from retrieval.retrieval_helpers.helpers import is_proximity_query
from retrieval.retrieval_helpers.helpers import find_boolean_operators
from retrieval.retrieval_helpers.helpers import is_phrase_bool
from retrieval.retrieval_helpers.helpers import database_retrieval
from retrieval.retrieval_helpers.helpers import set_proximity_values
from retrieval.retrieval_helpers.helpers import prepare_boolean_query
from retrieval.retrieval_models.bm25_model.bm25_model import Bm25_model
from retrieval.retrieval_models.vsm_model.vsm_model import Vsm_model
from retrieval.retrieval_helpers.helpers import json_loader
from retrieval.retrieval_helpers.helpers import apply_spellchecking
from retrieval.retrieval_helpers.helpers import seperate_mix

from retrieval.retrieval_helpers.helpers import date2doc_initializer
from retrieval.retrieval_models.language_model.language_model import Language_model
from retrieval.retrieval_models.proximity_retrieval.proximity_retrieval import proximity_retrieval
from retrieval.retrieval_models.boolean_retrieval.boolean_retrieval import boolean_retrieval
from retrieval.retrieval_helpers.index_compression import *
from retrieval.retrieval_helpers.index_decoder import *


class RetrievalExecution:

    print("loading in search dictionaries")
    word2byte = json_loader("retrieval/data/word2byte.json")
    word2byte_tf = json_loader("retrieval/data/word2byte_tf.json")
    date2doc = date2doc_initializer(json_loader("retrieval/data/date2doc.json"))
    doc_sizes = json_loader("retrieval/data/doc_sizes.json")

    print(f"date2doc size: {total_size(date2doc) / 1000000} mb")
    print(f"doc_sizes size: {total_size(doc_sizes) / 1000000} mb")
    print(f"word2byte size: {total_size(word2byte) / 1000000} mb")
    print(f"word2byte_tf size: {total_size(word2byte_tf) / 1000000} mb")

    abv_dict = abv_loader()

    def __init__(
            self,
            query,
            first_execution
    ):
        print("query:", query)
        preprocessing = Preprocessing()

        self.set_initial_values(query)

        self.abv_bool = False

        if is_proximity_query(query):
            self.proximity_query, self.proximity_value, self.pre_processed_query = set_proximity_values(query, preprocessing)
            return  # only working with query in the format #15(term1, term2) for now

        bool_operators = find_boolean_operators(query)
        if len(bool_operators) > 0:
            self.boolean_search, self.pre_processed_query, self.boolean_operators, self.positions_with_parentheses = prepare_boolean_query(query, bool_operators, preprocessing)
            return

        # pre process query
        self.pre_processed_query = []

        if not self.phrase_bool:
            initialising_time = datetime.datetime.now()
            query, self.has_term_been_corrected = spellcheck_query(
                query, self.abv_bool, first_execution,
                self.phrase_bool)  # only spell check query if it's not boolean or proximity retrieval
            self.corrected_query = query  # save the spellchecked query before pre processing it
            for q in query.split():
                self.pre_processed_query.append(preprocessing.apply_preprocessing(q))
            # print(f"spellchecking took {datetime.datetime.now() - initialising_time}")
        else:
            r = r'"(.*?)"'
            if re.split(r, query):
                terms = re.findall(r, query) + re.sub(r, '', query).split()
                terms = [i.strip() for i in terms if i]
                terms = list(filter(None, terms))
            else:
                terms = re.findall(r, query)
            for p in terms:
                self.pre_processed_query.append(preprocessing.apply_preprocessing(p))
        return

    def set_initial_values(self, query):
        self.initial_query = query
        self.has_term_been_corrected = False
        self.corrected_query = ""
        self.proximity_query = False
        self.boolean_search = False
        self.date_bool = False
        self.phrase_bool = is_phrase_bool(query)
        self.N = len(self.doc_sizes.keys())
        self.l_tot = sum(list(self.doc_sizes.values()))
        self.docs_in_date_range = []

    def mini_index_builder(self):

        start_time = datetime.datetime.now()

        self.mini_index = load_mini_index(self.pre_processed_query, "retrieval/data/final_index_tf.json", "retrieval/data/final_index.json", self.word2byte_tf, self.word2byte)

        #print(self.mini_index.keys())
        print(f"decompressing the index and decoding took {datetime.datetime.now() - start_time}")

        # check if mini_index is valid (at least one word of query is in the index)
        return self.valid_index()

    def get_date_range_union(self, start_date, end_date):
        doc_numbers = set()

        # get all dates in the range provided as a list of datetime objects
        date_range = pd.date_range(start_date, end_date).tolist()

        for date in date_range:
            date_docs_set = self.date2doc.get(date, set())
            doc_numbers = doc_numbers | date_docs_set

        return doc_numbers

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

    def bm25_ranking(self, bm25):
        ranked_articles = bm25.retrieval(self.pre_processed_query, self.mini_index, self.N, self.doc_sizes, self.l_tot,
                                     self.docs_in_date_range, self.date_bool)

        return ranked_articles

    def vsm_ranking(self):
        vsm = Vsm_model()
        ranked_docs = vsm.ranked_retrieval(self.pre_processed_query, self.mini_index, self.N, self.doc_sizes)
        return ranked_docs

    def lm_ranking(self, lm):

        ranked_articles = lm.retrieval(self.pre_processed_query, self.mini_index, self.N, self.doc_sizes, self.l_tot,
                                   self.docs_in_date_range, self.date_bool,
                                   use_pitman_yor_process=True)
        return ranked_articles

    def create_ranking_model_object(self, used_model):
        if used_model == "bm25":
            return Bm25_model()
        elif used_model == "lm":
            return Language_model(miu=1303, g=0.2)

    def execute_ranking(self, used_model, start_date, end_date):
        # returns false if none of the query terms match the index
        if self.mini_index_builder() == False:
            return False


        else: # if date filters are provided, get the date range doc union
            if start_date and end_date:
                self.docs_in_date_range = self.get_date_range_union(start_date, end_date)
                self.date_bool = True
            ranking_model_object = self.create_ranking_model_object(used_model)
            # document ranking
            start_time = datetime.datetime.now()
            if self.proximity_query:  # if we are doing a proximity query no need to check which model is used,
                # just retrieve the docs
                ranked_doc_numbers = proximity_retrieval(self.mini_index, self.proximity_value)
                ranked_article_objects = database_retrieval(ranked_doc_numbers)
                print(f"database retrieval took {datetime.datetime.now() - start_time}")
                return ranked_article_objects, self.has_term_been_corrected, self.corrected_query, self.initial_query
            elif self.boolean_search:

                doc_numbers = boolean_retrieval(self.boolean_operators, self.mini_index, self.N,
                                                       self.positions_with_parentheses, self.pre_processed_query)
                ranked_article_objects = ranking_model_object.retrieval(self.pre_processed_query, self.mini_index, self.N,
                                                                    self.doc_sizes, self.l_tot, self.docs_in_date_range,
                                                                    self.date_bool, doc_numbers)


                print(f"database retrieval took {datetime.datetime.now() - start_time}")
                return ranked_article_objects, self.has_term_been_corrected, self.corrected_query, self.initial_query

            if used_model == "bm25":
                ranked_articles = self.bm25_ranking(ranking_model_object)

            if used_model == "vsm":
                ranked_doc_numbers = self.vsm_ranking()

            if used_model == "lm":
                ranked_articles = self.lm_ranking(ranking_model_object)

            return ranked_articles, self.has_term_been_corrected, self.corrected_query, self.initial_query