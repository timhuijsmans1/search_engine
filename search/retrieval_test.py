print("importings")
from retrieval.retrieval_execution.retrieval_execution import RetrievalExecution
from retrieval.paths import *
print("finished imports")
if __name__ == "__main__":   
    query = "What is the stock price of facebook in the current shares market" 
    retrieval_execution = RetrievalExecution(query, INDEX_PATH, WORD2BYTE_PATH, DOC_SIZE_PATH, LINKS_PATH, 102485)
    doc_numbers = retrieval_execution.execute_ranking("bm25")
    
