from preprocessing import Preprocessing
from functions import read_index_from_file

class Vsm_model:
    pass



if __name__ == '__main__':
    preprocessor = Preprocessing()
    inverted_index = read_index_from_file("inverted_index.txt")
    queries = ["income tax reduction", "peace in the Middle East", "unemployment rate in UK",
               "industry in Scotland", "the industries of computers", "Microsoft Wdinows", "stock market in Japan",
               "the education with computers", "health industry", "campaigns of political parties"]

    term_inverted_indexes = {} # Dictionary to store the entries in the inverted index of each term in the query
    documents_appearing_in = {} # Dictionary to store the documents each term in the query appears in

    queries = [preprocessor.preprocess_query(query) for query in queries]

    test = 0