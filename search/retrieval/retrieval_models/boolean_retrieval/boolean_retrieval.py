from functools import reduce

import setuptools.command.install


def boolean_retrieval(boolean_operators, mini_index, N, positions_with_parentheses):
    """
    Boolean_operators: extracted boolean terms from preprocessing
    mini_index: constructed in retrieval_execution
    N: length of the index, used for creating list of all doc ids
    """
    terms_appearances = {}
    query_terms = list(mini_index.keys())
    for term in query_terms:
        terms_appearances[term] = mini_index[term][1].keys()  # mini_index[term][0] = number of appearances; mini_index[
        # term][1] = dictionary of documents and positions
    document_ids = apply_boolean_logic(terms_appearances, boolean_operators, N, positions_with_parentheses)
    return document_ids[:100]  # return only first 100


def apply_boolean_logic(terms_appearances, boolean_operators, N, positions_with_parentheses):
    all_doc_ids = range(1, N + 1)  # creating list of all documents ids, from 1 to N for using with "NOT"
    terms_in_query = list(terms_appearances.keys())  # getting the terms in the query
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
    else:
        if len(terms_in_query) == 2:  # apple AND NOT facebook
            return sorted(reduce(set.difference, map(set, terms_appearances.values())))
        else:
            documents_from_deconstructed_query = []  # example Greggs AND (Starbucks or Nandos) AND (Fifa OR Pes)
            # gets deconstructed into 3 separate lists of docs
            i = 0
            for element in terms_in_query:  # need to loop over elements in the query without an increasing "i" as
                # this screws up the positioning
                position = i
                if i in positions_with_parentheses:
                    term1 = terms_in_query[position]
                    term2 = terms_in_query[position + 1]
                    term1_appearances = terms_appearances[term1]
                    term2_appearances = terms_appearances[term2]
                    if boolean_operators[position] == "OR":
                        documents_from_deconstructed_query.append(
                            list(set(term1_appearances)) + list(set(term2_appearances)))
                    elif boolean_operators[position] == "AND":
                        documents_from_deconstructed_query.append(
                            set.intersection(set(term1_appearances), set(term2_appearances)))
                    elif boolean_operators[position] == "NOT":
                        documents_from_deconstructed_query.append(
                            set.difference(set(term1_appearances), set(term2_appearances)))
                    i += 2  # adding two as we worked with the first and following terms
                    if i == len(terms_in_query): # check if final term in query
                        break
                else:
                    term = terms_in_query[position]
                    documents_from_deconstructed_query.append(terms_appearances[term])
                    i += 1
                    if i >= len(terms_in_query):
                        break
            positions_without_parantheses = [position for position in range(len(boolean_operators)) if position not in positions_with_parentheses]
            main_operators = [boolean_operators[i] for i in positions_without_parantheses]
            documents_to_be_returned = []
            for idx, operator in enumerate(main_operators):
                if operator == "OR":
                    if not documents_to_be_returned:
                        union = set.union(set(documents_from_deconstructed_query[idx]), set(documents_from_deconstructed_query[idx + 1]))
                    else:
                        union = set.union(set(documents_to_be_returned), set(documents_from_deconstructed_query[idx+1]))
                    documents_to_be_returned = list(union)
                elif operator == "AND":
                    if not documents_to_be_returned:
                        intersection = set.intersection(set(documents_from_deconstructed_query[idx]), set(documents_from_deconstructed_query[idx+1]))
                    else:
                        intersection = set.intersection(set(documents_to_be_returned), set(documents_from_deconstructed_query[idx+1]))
                    documents_to_be_returned = list(intersection)
                elif operator == "NOT":
                    if not documents_to_be_returned:
                        difference = set.difference(set(documents_from_deconstructed_query[idx]), set(documents_from_deconstructed_query[idx+1]))
                    else:
                        difference = set.difference(set(documents_to_be_returned), set(documents_from_deconstructed_query[idx+1]))
                    documents_to_be_returned = list(difference)
            documents_to_be_returned = list(sorted(set(documents_to_be_returned)))
            return documents_to_be_returned








