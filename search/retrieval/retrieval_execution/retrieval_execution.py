import json
import numpy as np
import datetime
import sys

from retrieval.models import Article
from retrieval.retrieval_helpers.preprocessing import Preprocessing
from retrieval.retrieval_helpers.helpers import write_results_to_file
from retrieval.retrieval_helpers.helpers import is_proximity_query
from retrieval.retrieval_helpers.helpers import find_boolean_operators
from retrieval.retrieval_models.bm25_model.bm25_model import Bm25_model
from retrieval.retrieval_models.vsm_model.vsm_model import Vsm_model
from retrieval.retrieval_models.language_model.language_model import Language_model
from retrieval.retrieval_models.proximity_retrieval.proximity_retrieval import proximity_retrieval
from retrieval.retrieval_models.boolean_retrieval.boolean_retrieval import boolean_retrieval

class RetrievalExecution:
    
    print("loading in the index, please wait for the app to start up")
    with open("retrieval/data/index.json", "r") as index_handle:
        inverted_index = json.load(index_handle)
    print(f"loaded the index with a size of {sys.getsizeof(inverted_index)} bytes")
    
    with open("retrieval/data/doc_sizes.json", 'r') as doc_size_handle:
        doc_sizes = json.load(doc_size_handle)

    def __init__(
            self, 
            query, 
            total_doc_number,
        ):

        preprocessing = Preprocessing()

        self.N = total_doc_number
        if '"' in query:
            self.phrase_bool = True
        else:
            self.phrase_bool = False

        self.proximity_query = False # defining it before checking - if check fails have flag for checking before
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
            self.pre_processed_query, self.boolean_operators = preprocessing.preprocess_boolean_query(query, bool_operators)
            return

        # pre process query
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
        self.mini_index = {}

        start_time = datetime.datetime.now()

        for word in self.pre_processed_query:
            if word in self.inverted_index:
                decoded_list = self.delta_decoder(self.inverted_index[word])
                self.mini_index[word] = decoded_list

        print(f"building the mini index and decoding took {datetime.datetime.now() - start_time}")

        # check if mini_index is valid (at least one word of query is in the index)
        return self.valid_index()

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

        self.l_tot = np.sum(np.array(list(self.doc_sizes.values())))

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
    
    def execute_ranking(self, used_model):
        # returns false if none of the query terms match the index
        if self.mini_index_builder() == False:
            return False

        else:

            # document ranking
            start_time = datetime.datetime.now()

            if self.proximity_query:  # if we are doing a proximtiy query no need to check which model is used,
                # just retrieve the docs
                ranked_doc_numbers = proximity_retrieval(self.mini_index, self.proximity_value)
                ranked_article_objects = self.database_retrieval(ranked_doc_numbers)
                print(f"database retrieval took {datetime.datetime.now() - start_time}")
                return ranked_article_objects
            elif self.boolean_search:
                ranked_doc_numbers = boolean_retrieval(self.boolean_operators, self.mini_index, self.N)
                ranked_article_objects = self.database_retrieval(ranked_doc_numbers)
                print(f"database retrieval took {datetime.datetime.now() - start_time}")
                return ranked_article_objects

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

            return ranked_article_objects
