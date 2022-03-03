from functools import reduce


def boolean_retrieval(boolean_operators, mini_index, N):
    """
    Boolean_operators: extracted boolean terms from preprocessing
    mini_index: constructed in retrieval_execution
    N: length of the index, used for creating list of all doc ids
    """
    terms_appearances = {}
    query_terms = list(mini_index.keys())
    for term in query_terms:
        print(term)
        terms_appearances[term] = mini_index[term][1].keys() # mini_index[term][0] = number of appearances; mini_index[
        print(len(terms_appearances[term]))
        # term][1] = dictionary of documents and positions
    document_ids = apply_boolean_logic(terms_appearances, boolean_operators, N)
    return document_ids[:100]  # return only first 100


def apply_boolean_logic(terms_appearances, boolean_operators, N):
    all_doc_ids = range(1, N+1) # creating list of all documents ids, from 1 to N for using with "NOT"
    if len(boolean_operators) == 1:
        if boolean_operators[0] == "OR":
            doc_ids = sorted(reduce(set.union, map(set, terms_appearances.values())))
            return sorted(doc_ids)
        if boolean_operators[0] == "AND":
            doc_ids = sorted(reduce(set.intersection, map(set, terms_appearances.values())))
            return doc_ids
        elif boolean_operators[0] == "NOT" or "AND NOT":
            if len(terms_appearances) == 1:  # only one term, eg: "NOT apple"
                print(terms_appearances.keys())
                doc_ids = reduce(set.difference, map(set, terms_appearances.values()), all_doc_ids)
                return sorted(doc_ids)
    else:  # apple AND NOT facebook
        print("we are here")
        return sorted(reduce(set.difference, map(set, terms_appearances.values())))
