import json
import numpy as np
import datetime
import sys
import pandas as pd

from retrieval.models import Article
from retrieval.retrieval_helpers.index_loader import load_mini_index
from retrieval.retrieval_helpers.preprocessing import Preprocessing
from retrieval.retrieval_helpers.helpers import write_results_to_file
from retrieval.retrieval_models.bm25_model.bm25_model import Bm25_model
from retrieval.retrieval_models.vsm_model.vsm_model import Vsm_model
from retrieval.retrieval_helpers.helpers import json_loader
from retrieval.retrieval_helpers.helpers import date2doc_initializer
from retrieval.retrieval_models.language_model.language_model import Language_model

class RetrievalExecution:
    
    print("loading in search dictionaries, please wait for the app to start up")
    word2byte = json_loader("retrieval/data/word2byte.json")
    date2doc = date2doc_initializer(json_loader("retrieval/data/date2doc.json"))
    doc_sizes = json_loader("retrieval/data/doc_sizes.json")
    print("done loading all startup files")

    def __init__(
            self, 
            query, 
            total_doc_number,
        ):

        if '"' in query:
            self.phrase_bool = True
        else:
            self.phrase_bool = False

        self.N = total_doc_number

        # pre process query
        preprocessing = Preprocessing()
        self.pre_processed_query = preprocessing.apply_preprocessing(query)

        return

    def delta_decoder(self, delta_encoded_inverted_list):
        """
        input params:
        v_byte_encoded_inverted_list : dictionary
            one key being the word, and values a list with delta encoded doc_id and decoded positions

        return:
        inverted list in its original format {word: [document_count, {doc_number: [positions]}}
        """
        doc_count, delta_pos_combos = delta_encoded_inverted_list # int, list
        list_out = [doc_count, {}]

        # add the first doc number manually
        current_doc_num, positions = delta_pos_combos[0] # int, list
        list_out[1][current_doc_num] = positions # add doc and pos to doc_pos dict

        for delta_pos_combo in delta_pos_combos[1:]:
            delta, positions = delta_pos_combo
            current_doc_num = current_doc_num + delta
            list_out[1][current_doc_num] = positions

        return list_out

    def mini_index_builder(self):

        start_time = datetime.datetime.now()

        self.mini_index = load_mini_index(self.pre_processed_query, "retrieval/data/index_dict.json", self.word2byte)

        print(f"building the mini index and decoding took {datetime.datetime.now() - start_time}")
        print(self.mini_index.keys())

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
            print("no results")
            return False
        else:
            return True

    def bm25_ranking(self):

        bm25 = Bm25_model()

        self.l_tot = sum(list(self.doc_sizes.values()))

        if self.phrase_bool:
            ranked_docs = bm25.phrase_rank(self.pre_processed_query, self.mini_index, self.N, self.doc_sizes, self.l_tot)
        else:
            ranked_docs = bm25.rank(self.pre_processed_query, self.mini_index, self.N, self.doc_sizes, self.l_tot)

        return ranked_docs

    def vsm_ranking(self):
        vsm = Vsm_model()
        ranked_docs = vsm.ranked_retrieval(self.pre_processed_query, self.mini_index, self.N, self.doc_sizes)
        return ranked_docs

    def lm_ranking(self):
        lm = Language_model(miu=1303, g=0.2)
        l_tot = np.sum(np.array(list(self.doc_sizes.values())))

        if self.phrase_bool:
            ranked_docs = lm.phrase_retrieval(self.pre_processed_query, self.mini_index, self.N, self.doc_sizes, l_tot)
        else:
            ranked_docs = lm.retrieval(self.pre_processed_query, self.mini_index, self.N, self.doc_sizes, l_tot, use_pitman_yor_process=True)
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
            if used_model == "bm25":
                ranked_doc_numbers = self.bm25_ranking()
            
            if used_model == "vsm":
                ranked_doc_numbers = self.vsm_ranking()

            if used_model == "lm":
                ranked_doc_numbers = self.lm_ranking()
            
            start_time = datetime.datetime.now()
            # these can be re-ordered according to their date
            ranked_article_objects = self.database_retrieval(ranked_doc_numbers)
            print(f"database retrieval took {datetime.datetime.now() - start_time}")

            return ranked_article_objects
