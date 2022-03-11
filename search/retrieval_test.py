from retrieval.retrieval_execution.retrieval_execution_performance import RetrievalExecution

if __name__ == "__main__":   
    query = "What is the stock price of facebook in the current shares market" 
    retrieval_execution = RetrievalExecution(query, True)
    doc_numbers = retrieval_execution.execute_ranking("bm25", None, None)
