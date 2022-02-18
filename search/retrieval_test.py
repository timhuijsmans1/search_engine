from retrieval.retrieval_execution.retrieval_execution import RetrievalExecution

if __name__ == "__main__":   
    query = "What is the stock price of facebook in the current shares market" 
    retrieval_execution = RetrievalExecution(query, 102485)
    doc_numbers = retrieval_execution.execute_ranking("bm25")
    
