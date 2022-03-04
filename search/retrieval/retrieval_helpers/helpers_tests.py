import search.retrieval.retrieval_models.boolean_retrieval.boolean_retrieval
from helpers import find_boolean_operators
from preprocessing import Preprocessing

if __name__ == '__main__':
    query1 = "greggs OR (costa AND macbook) OR (fifa AND pasta)"
    query2 = "greggs AND macbook AND pasta"
    preprocessor = Preprocessing()
    boolean_operators_present = find_boolean_operators(query1)
    terms, boolean_operators, positions = preprocessor.preprocess_boolean_query(query1, boolean_operators_present)
    stop = 0
