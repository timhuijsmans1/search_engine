import json
import re
import csv
import pandas as pd

from datetime import datetime
from textblob import TextBlob
from spellchecker import SpellChecker

import line_profiler
import atexit

profile = line_profiler.LineProfiler()
atexit.register(profile.print_stats)


def helper_example():
    # do something
    return None

def abv_loader():
    abv_dict = {}
    with open("retrieval/data/Fin_abbv.csv", 'r') as fin_abbv:
        abbv_temp = csv.reader(fin_abbv)
        for a, m in abbv_temp:
            abv_dict[a] = m
    return abv_dict

def date2doc_initializer(date2doc_string):
    date2doc_obj = {}
    for date_string in date2doc_string:
        date_obj = datetime.strptime(date_string.strip(' 00:00:00'), '%Y%m%d')
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

def consecutive_occ(inverted_index_doc):

    tot = len(inverted_index_doc)
    tot_app = sorted(sum(inverted_index_doc, []))  # Main Assumption that one word is not occurring twice in a row
    # Tot app returns the sorted list of document positions

    count = 0
    consecutive = 0

    for i in range(len(tot_app) - 1):
        if (tot_app[i + 1] - tot_app[i]) == 1:
            for t in range(tot - 1):
                if tot_app[i] in inverted_index_doc[t] and tot_app[i + 1] in inverted_index_doc[t + 1]:
                    count += 1
                    if count == (tot - 1):
                        consecutive += 1
                        count = 0
        else:
            count = 0
    return consecutive

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


def split_list(a_list):
    half = len(a_list)//2
    return a_list[:half], a_list[half:]

def spellcheck_query(query, is_finance_abbreviation, is_first_run, is_phrase_bool):
    # this will be executed if the user is not re-running for the uncorrected query
    if is_first_run:
        spell = SpellChecker()
        corrected_query = []
        nyse_listed = pd.read_csv("retrieval/retrieval_helpers/nyse_listed_companies.csv")
        # if is_phrase_bool:
        #     r = r'"(.*?)"'
        #     if re.split(r, query):
        #         phrases = re.findall(r, query) + re.sub(r, '', query).split()
        #         phrases = [i.strip() for i in phrases if i]
        #         phrases = list(filter(None, phrases))
        #         for phrase in phrases:
        #             terms_in_phrase = phrase.split()
        #             corrected_phrase = []
        #             for term in terms_in_phrase:
        #                 term = apply_spellchecking(term, nyse_listed, is_finance_abbreviation, spell)
        #                 corrected_phrase.append(term)
        #             corrected_phrase = " ".join(str(term) for term in corrected_phrase)
        #             corrected_phrase = f'"{corrected_phrase}"'
        #             corrected_query.append(corrected_phrase)
        #         corrected_query = " ".join(str(phrase) for phrase in corrected_query)
        #     else:
        #         terms = re.findall(r, query)
        # else:
        query = query.split()  # query comes in as string
        for term in query:
            term = apply_spellchecking(term, nyse_listed, is_finance_abbreviation, spell)
            corrected_query.append(term)
        corrected_query = " ".join(str(term) for term in corrected_query)  # convert back to string so no problems with preprocessing
        query = " ".join(str(term) for term in query)
        has_term_been_corrected = True if query != corrected_query else False
        return corrected_query, has_term_been_corrected

    # if the user just wants to run the uncorrected query, this will be executed
    else:
        return query, False

def pre_process_nasdaq_list():
    nyse_listed = pd.read_csv("retrieval/retrieval_helpers/nasdaq_screener.csv")
    nyse_listed['Symbol'] = nyse_listed['Symbol'].str.lower()
    nyse_listed['Name'] = nyse_listed['Name'].str.lower()
    nyse_listed.to_csv("nyse_listed_companies.csv")


def is_phrase_bool(query):
    if '"' in query:
        return True
    return False

def add_abv_expansion(query, abv_dict):

    for t in query.split():
        abv_dict_keys = [i.rstrip() for i in abv_dict.keys()]
        if t.upper() in abv_dict_keys:
            query += (f' "{abv_dict[t.upper()]}"')
    return query


def set_proximity_values(query, preprocessor):
    is_proximity_query_bool = True
    proximity_value, preprocessed_query = preprocessor.preprocess_proximity_query(query)
    return is_proximity_query_bool, proximity_value, preprocessed_query


def prepare_boolean_query(query, bool_operators, preprocessor):
    boolean_search = True
    preprocessed_boolean_query, boolean_operators, positions_with_parentheses = preprocessor.preprocess_boolean_query(
        query, bool_operators)
    return boolean_search, preprocessed_boolean_query, boolean_operators, positions_with_parentheses


def apply_spellchecking(term, nyse_listed, is_finance_abbreviation, spell):
    if term in nyse_listed['Symbol'].values:  # check if term is an abbreviation of common stock
        term = nyse_listed.loc[nyse_listed['Symbol'] == term, 'Name'].item()
        return term
    elif nyse_listed['Name'].str.contains(
            term).any() or is_finance_abbreviation:  # check if the term is in the full name of the company -
        # example berkshire would get corrected to something irrelevant
        # or finance abbreviation such as ytm
        return term
    else:
        corrected_term = spell.correction(term)
    return corrected_term

