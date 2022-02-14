import json

# from retrieval.retrieval_helpers.index_loader import load_mini_index
# from retrieval.retrieval_helpers.preprocessing import Preprocessing
### imports working for Vlad's machine
from search.retrieval.retrieval_models.vsm_model.vsm_model import Vsm_model
from search.retrieval.retrieval_helpers.preprocessing import Preprocessing
from search.retrieval.retrieval_helpers.index_loader import load_mini_index
from search.retrieval.retrieval_models.bm25_model.bm25_model import Bm25_model
###
# from retrieval.retrieval_models.bm25_model.bm25_model import Bm25_model
# from retrieval.retrieval_models.vsm_model.vsm_model import Vsm_model


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

        # pre-process query
        preprocessing = Preprocessing()
        self.pre_processed_query = preprocessing.apply_preprocessing(query)
        
        # ideally, these two open-statements will be executed upon starting to type a query
        # load hash (dict: {word: [start_byte, bytes_to_read])
        with open(word2byte_path, 'r') as hash_handle:
            self.word2byte = json.load(hash_handle)

        # load doc_sizes (dict: {doc_id: size})
        with open(doc_size_path, 'r') as doc_size_handle:
            self.doc_sizes = json.load(doc_size_handle)

        # store total doc number (int)
        self.N = total_doc_number

        # load mini index with hash (this is a normal index, only containing query words)
        self.mini_index = load_mini_index(self.pre_processed_query, index_path, self.word2byte)

        print("did the slow stuff")

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
        #TODO GHADI
        # implement the bm25 ranking. At this point, you can use all the initialized data build above.

        # The mini index is an index only consisting of those words from the query that appeared in the 
        # index. The format of the mini_index is consistent with previous format of the entire index:
        # mini_index[word] = [number_of_appearances, {document1: [position1, position2, ...], document2: [position1, position2, ...]}]

        # this function should return a list of the ranked documents
        return

    def vsm_ranking(self):
        vsm = Vsm_model()
        #TODO VLAD
        # implement the vsm ranking. At this point, you can use all the initialized data build above.

        # We need N, the total size of our collection

        # The mini index is an index only consisting of those words from the query that appeared in the 
        # index. The format of the mini_index is consistent with previous format of the entire index:
        # mini_index[word] = [number_of_appearances, {document1: [position1, position2, ...], document2: [position1, position2, ...]}]

        vsm.ranked_retrieval(self.pre_processed_query, self.mini_index, self.N, self.doc_sizes)

        # this function should return a list of the ranked documents
        return
    
    def execute_ranking(self, used_model):

        # if index is empty, do not start retrieval models
        if not self.valid_index():
            return False

        if used_model == "bm25":
            ranked_doc_numbers = self.bm25_ranking()
        
        if used_model == "vsm":
            ranked_doc_numbers = self.vsm_ranking()
        
        # hard code just a list of max 10 document numbers
        first_word_in_index = list(self.mini_index.keys())[0]
        some_doc_numbers = list(self.mini_index[first_word_in_index][1].keys())
        some_doc_ints = [int(doc_id) for doc_id in some_doc_numbers]

        return some_doc_ints