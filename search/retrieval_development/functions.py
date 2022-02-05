import re
from typing import Union, Any

from preprocessing import Preprocessing


def read_text_file(filepath):
    with open(filepath) as f:
        lines = f.readlines()
        return lines


def read_index_from_file(filepath):
    """
    Function to read the positional inverted index from file

    Format of the index: positional_index[word] = [number_of_appearances,
                                                    {document1: [position1, position2, ...],
                                                    document2: [position1, position2, ...]}
                                                    ]
    """
    number_pattern = r'[0-9]+'  # regex
    inverted_index_dict = {}
    with open(filepath) as f:
        # is_new_term flags the first entry in the document which will represent a term
        # and its total number of appearances
        is_new_term = True
        lines = f.readlines()
        for line in lines:
            if line == '\n':
                # whitespace between every new term entrance in the file and a previous one
                is_new_term = True
                continue
            if is_new_term:
                line = line.split(':')
                term = line[0]
                occurences_in_file = int(line[1])
                inverted_index_dict[term] = [occurences_in_file]
                # Setting the flag to false to process the following lines which contain the positions of the term in
                # each document it appears in
                is_new_term = False
            else:
                document_entries = re.findall(number_pattern, line)  # extracting ony number to get rid of ":" and new
                # line characters
                document_id = int(document_entries[0])  # first entry is document id
                positions = document_entries[1:]  # rest of entries are positions in the doc
                positions = [int(position) for position in positions]  # converting to integer
                inverted_index_dict[term].append({})
                inverted_index_dict[term][1][document_id] = positions
    return inverted_index_dict


def get_term_entry_from_inverted_index(inverted_index, term):
    if term in inverted_index:
        inverted_index_term = inverted_index[term]
        return inverted_index_term


def extract_all_documents_term_appears_in(inverted_index_term):
    """
    Function to get all the documents the term has appeared in
    Extracted from the inverted index
    """
    documents_term_appears_in = []
    for k, v in inverted_index_term.items():  # key = documentNo, value = number of appearances
        # Can throw "Attribute Error: 'NoneType' object has no attribute items
        documents_term_appears_in.append(k)
    return documents_term_appears_in


def create_doc_dictionary(element_tree, preprocessor):
    """
    Function to create a document dictionary from a given XML Element Tree
    Loops over all elements in the tree
    If the element tag is "DOCNO", then a new entry is created in the dictionary with the key as the document number
    Else, if the element tag is "HEADLINE" or "TEXT", the value for the newly created key is stored appended with the text
    The function returns the dictionary with all key, value pairs encountered

    """
    current_document = 0
    document_dict: dict[Union[int, Any], list[Any]] = {}
    for elt in element_tree.iter():
        if elt.tag == "DOCNO":
            current_document = int(elt.text)
            document_dict[current_document] = []
        elif elt.tag == "HEADLINE" or elt.tag == "TEXT":
            document_dict[current_document].append(elt.text)
    for key, value in document_dict.items():
        document_dict[key] = preprocessor.apply_preprocessing(document_dict[key])
    return document_dict
