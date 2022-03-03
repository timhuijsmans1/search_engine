import search.retrieval.retrieval_models.boolean_retrieval.boolean_retrieval
from helpers import find_boolean_operators
from preprocessing import Preprocessing

if __name__ == '__main__':
    query1 = "greggs AND NOT starbucks"
    query2 = "#10(greggs, starbucks)"
    preprocessor = Preprocessing()
    boolean_operators_present = find_boolean_operators(query1)
    print(len(boolean_operators_present))
    terms, boolean_operators = preprocessor.preprocess_boolean_query(query1, boolean_operators_present)
    proximity_value, query = preprocessor.preprocess_proximity_query(query2)
    print(terms)
    print(boolean_operators)
    print(query)