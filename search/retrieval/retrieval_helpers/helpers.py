import json
import re
from datetime import datetime

import pandas as pd
from textblob import TextBlob

from spellchecker import SpellChecker


def helper_example():
    # do something
    return None


def date2doc_initializer(date2doc_string):
    date2doc_obj = {}
    for date_string in date2doc_string:
        date_obj = datetime.strptime(date_string.strip(' 00:00:00'), '%Y-%m-%d')
        doc_set = set(date2doc_string[date_string])
        date2doc_obj[date_obj] = doc_set
    return date2doc_obj


def read_text_file(filepath):
    with open(filepath) as f:
        lines = f.readlines()
        return lines


def json_loader(path):
    with open(path, "r") as f:
        output = json.load(f)

    return output


def date_checker(date_start, date_end):
    now = datetime.now()

    # check if dates are in expected format and valid
    try:
        date_start_obj = datetime.strptime(date_start, '%m/%d/%Y')
        date_end_obj = datetime.strptime(date_end, '%m/%d/%Y')
    except:
        return False, None, None

    # check if start is before end date
    if date_end_obj < date_start_obj:
        return False, None, None

    # check if date interval starts in the past or today
    if date_start_obj > now:
        return False, None, None

    return True, date_start_obj, date_end_obj


def extract_all_documents_term_appears_in(mini_index_term):
    """
    Function to extract all the term has appeared in
    Mini_index_term - only the mini-index entry for the specific term
    Returns: documents_term_appears_in
    """

    documents_term_appears_in = []
    for k, v in mini_index_term.items():  # key = documentNo, value = number of appearances
        # can throw "Attribute Error: 'NoneType' object has no attribute items
        documents_term_appears_in.append(k)
    return documents_term_appears_in


def write_results_to_file(ranked_docs, used_model, pre_processed_query):
    filename = used_model
    for term in pre_processed_query:
        filename = filename + " " + term
    filename = filename + ".txt"
    filename = "retrieval/retrieval_results/" + filename
    with open(filename, 'w') as f:
        print(filename)
        for term in pre_processed_query:
            f.write(term)
            f.write(" ")
        f.write("\n")
        for doc_id in ranked_docs:
            f.write("%d\n" % doc_id)


def sort_document_scores(document_scores):
    sorted_document_scores = sorted(document_scores.items(), key=lambda x: x[1], reverse=True)
    sorted_document_ids = [id_score[0] for id_score in sorted_document_scores[:100]]
    return sorted_document_ids


def is_proximity_query(query):
    proximity_query_pattern = r'^#(\d+)'  # finds the hashtag in the query
    is_proximity_query_bool = bool(re.findall(proximity_query_pattern, query))
    return is_proximity_query_bool


def find_boolean_operators(query):
    boolean_keywords = ["AND", "NOT", "OR"]
    boolean_operators_present = re.findall(r"(?=(" + '|'.join(boolean_keywords) + r"))",
                                           query)  # TO DO: Maybe change to "if term in query" more readable - this implementation works with more than 1 AND, OR etc.
    return boolean_operators_present


def spellcheck_query(query, is_finance_abbreviation, is_phrase_bool):
    spell = SpellChecker()
    corrected_query = []
    has_term_been_corrected = False  # flag for knowing if we should display message to user in view
    query = query.split()  # query comes in as string
    nyse_listed = pd.read_csv("retrieval/retrieval_helpers/nyse_listed_companies.csv")
    for term in query:
        if term in nyse_listed['Symbol'].values:  # check if term is an abbreviation of common stock
            term = nyse_listed.loc[nyse_listed['Symbol'] == term, 'Name'].item()
            corrected_query.append(term)
        elif nyse_listed['Name'].str.contains(
                term).any() or is_finance_abbreviation or is_phrase_bool:  # check if the term is in the full name of
            # the company -
            # example berkshire would get corrected to something irrelevant
            # or finance abbreviation such as ytm
            corrected_query.append(term)
        else:
            corrected_term = spell.correction(term)
            corrected_query.append(corrected_term)
            has_term_been_corrected = True if corrected_term != term else False

    corrected_query = " ".join(
        str(term) for term in corrected_query)  # convert back to string so no problems with preprocessing
    return corrected_query, has_term_been_corrected


def pre_process_nasdaq_list():
    nyse_listed = pd.read_csv("retrieval/retrieval_helpers/nasdaq_screener.csv")
    nyse_listed['Symbol'] = nyse_listed['Symbol'].str.lower()
    nyse_listed['Name'] = nyse_listed['Name'].str.lower()
    nyse_listed.to_csv("nyse_listed_companies.csv")


def is_phrase_bool(query):
    if '"' in query:
        return True
    return False

def set_abv_bool_values(query, abv_dict):
    query_abv = ""
    abv_bool = False
    for t in query.split():
        abv_dict_keys = [i.rstrip() for i in abv_dict.keys()]
        if t.upper() in abv_dict_keys:
            query_abv = abv_dict[t.upper()]
            abv_bool = True
    return query_abv, abv_bool


def set_proximity_values(query, preprocessor):
    is_proximity_query_bool = True
    proximity_value, preprocessed_query = preprocessor.preprocess_proximity_query(query)
    return is_proximity_query_bool, proximity_value, preprocessed_query


def prepare_boolean_query(query, bool_operators, preprocessor):
    boolean_search = True
    preprocessed_boolean_query, boolean_operators, positions_with_parentheses = preprocessor.preprocess_boolean_query(
        query, bool_operators)
    return boolean_search, preprocessed_boolean_query, boolean_operators, positions_with_parentheses

def apply_spellchecking(query, abv_bool, phrase_bool):
    has_term_been_corrected = False
    query, has_term_been_corrected = spellcheck_query(query, abv_bool, phrase_bool)
    corrected_query = query
    return query, has_term_been_corrected, corrected_query

