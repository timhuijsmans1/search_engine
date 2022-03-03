import json

from datetime import datetime

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
    for k, v in mini_index_term.items(): # key = documentNo, value = number of appearances
        # can throw "Attribute Error: 'NoneType' object has no attribute items
        documents_term_appears_in.append(k)
    return documents_term_appears_in


def write_results_to_file(ranked_docs, used_model, pre_processed_query):
    filename = used_model
    for term in pre_processed_query:
        filename = filename + " " + term
    filename = filename + ".txt"
    filename = "retrieval/retrieval_results/" + filename
    print("writing results to file")
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
    print(sorted_document_scores[:10])
    sorted_document_ids = [id_score[0] for id_score in sorted_document_scores[:100]]
    return sorted_document_ids