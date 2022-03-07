def check_if_terms_in_proximity(term1_positions_in_doc, term2_positions_in_doc, proximity_value, doc_id):
    """
    Function to loop over all position of term1 in given doc and term 2 in given doc comparing differences between positions
    When doc matches given proximtiy_value, return doc id
    """
    for term1_position in term1_positions_in_doc:
        for term2_position in term2_positions_in_doc:
            if abs(term1_position - term2_position) <= proximity_value:  # using absolute difference for proximity retrieval
                return doc_id


def proximity_retrieval(mini_index, proximity_value):
    # extract each index separately - main assumption we only have two terms
    query_terms = list(mini_index.keys())
    term1_inverted_index = mini_index[query_terms[0]]
    term2_inverted_index = mini_index[query_terms[1]]

    term1_positions_dict = term1_inverted_index[1]
    term2_positions_dict = term2_inverted_index[1]

    common_docs = term1_positions_dict.keys() & term2_positions_dict.keys()
    common_docs = sorted(common_docs)

    documents_where_terms_are_in_proximity = []

    for doc_id in common_docs:
        term1_positions_in_doc = term1_positions_dict[doc_id]
        term2_positions_in_doc = term2_positions_dict[doc_id]

        doc_in_proximity = check_if_terms_in_proximity(term1_positions_in_doc, term2_positions_in_doc, proximity_value,
                                                       doc_id)
        documents_where_terms_are_in_proximity.append(doc_in_proximity)
    # The list will contain some none elements based on the return of check_if_terms_in_proximity
    documents_where_terms_are_in_proximity = [doc for doc in documents_where_terms_are_in_proximity if doc is not None]
    return documents_where_terms_are_in_proximity
