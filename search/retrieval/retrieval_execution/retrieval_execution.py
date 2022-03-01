import json
import numpy as np
import datetime
import sys

from retrieval.retrieval_helpers.preprocessing import Preprocessing
from retrieval.retrieval_helpers.helpers import write_results_to_file
from retrieval.retrieval_models.bm25_model.bm25_model import Bm25_model
from retrieval.retrieval_models.vsm_model.vsm_model import Vsm_model
from retrieval.retrieval_models.language_model.language_model import Language_model

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
        inverted list in its original format {word: [document_count, [[doc_number, [positions]]]}
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
        # if the index is valid (at least one word of query is in the index)
        for word in self.pre_processed_query:
            if word in self.inverted_index:
                decoded_list = self.delta_decoder(self.inverted_index[word])
                self.mini_index[word] = decoded_list
        print(f"building the mini index and decoding took {datetime.datetime.now() - start_time}")

        return self.valid_index()

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

        # self.l_tot = 0
        # for d in self.doc_sizes.values():
        #     self.l_tot += int(float(d))
        #

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

        # otherwise, execute the desired search model with the query and mini index
        else:
            start_time = datetime.datetime.now()
            if used_model == "bm25":
                ranked_doc_numbers = self.bm25_ranking()
            
            if used_model == "vsm":
                ranked_doc_numbers = self.vsm_ranking()
            if used_model == "lm":
                ranked_doc_numbers = self.lm_ranking()
            print(f"retrieval took {datetime.datetime.now() - start_time}")
            write_results_to_file(ranked_doc_numbers[:20], used_model, self.pre_processed_query)  # writing top 20 doc ids to file for easier comparison

            return ranked_doc_numbers