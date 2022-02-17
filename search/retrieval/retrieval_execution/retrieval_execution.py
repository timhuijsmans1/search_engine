import json
import numpy as np
import datetime

from retrieval.retrieval_helpers.preprocessing import Preprocessing
from retrieval.retrieval_helpers.index_loader import load_mini_index
from retrieval.retrieval_models.bm25_model.bm25_model import Bm25_model
from retrieval.retrieval_models.vsm_model.vsm_model import Vsm_model

class RetrievalExecution:

    def __init__(
            self, 
            query, 
            index_path,
            word2byte_path,
            doc_size_path,
            link_path,
            total_doc_number,
        ):
        self.start_time = datetime.datetime.now()
        # pre-process query
        if '"' in query:
            self.phrase_bool = True
        else:
            self.phrase_bool = False

        preprocessing = Preprocessing()
        self.pre_processed_query = preprocessing.apply_preprocessing(query)

        with open(word2byte_path, 'r') as hash_handle:
            self.word2byte = json.load(hash_handle)

        print(f"loaded word2byte ({datetime.datetime.now() - self.start_time})")

        # load doc_sizes (dict: {doc_id: size})
        with open(doc_size_path, 'r') as doc_size_handle:
            self.doc_sizes = json.load(doc_size_handle)

        # store total doc number (int)
        self.N = total_doc_number

        # load mini index with hash (this is a normal index, only containing query words)
        self.mini_index = load_mini_index(self.pre_processed_query, index_path, self.word2byte)
        print(f"loaded and decoded index ({datetime.datetime.now() - self.start_time})")
        return

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
        # mini_index[word] = [number_of_appearances, {document1: [position1, position2, ...], document2: [position1, position2, ...]}]

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
    
    def execute_ranking(self, used_model):

        # if index is empty, do not start retrieval models
        if not self.valid_index():
            return False

        if used_model == "bm25":
            ranked_doc_numbers = self.bm25_ranking()
        
        if used_model == "vsm":
            ranked_doc_numbers = self.vsm_ranking()
        print(f"loaded and decoded index and word2byte and retrieved docs ({datetime.datetime.now() - self.start_time})")
        return ranked_doc_numbers