import json 
import bson

def delta_encoder(inverted_positional_list, new_doc_number):
    """
    v-byte decode the current string (v-byte decode function below)
    sum all the v-byte decoded deltas to get the previous doc number
    calculate delta encoded doc number 

    return
    delta encoded doc number, ready for v-byte encoding
    """
    return

def v_byte_encoder(doc_delta, positions, appearances):
    """
    return:
    v-byte encoded doc number delta and position (doc_num, position)
    """
    return

def index_extender(text_body, index, doc_number):
    """
    input params:
    text_body : list
        list of all the pre-processed tokens in a text body
    index : dictionary
        the current index with lists delta and v-byte encoded

    for each word in body
        check if word is in the index
            if in the index:
                delta encode the doc id of the new word based on all the previous doc numbers
                v-byte encode the document count, delta and positions
                add delta and position to the file
            else:
                v_byte encode doc number and position
                make new inverted list 
    """

    return

def index_builder():
    """
    initialise empty index
    
    for all urls:
        get the text body
        pre-process text body
        run index extender function
    """
    index = {}

    # !!! manually getting some text bodys for testing, update this to url retrieval
    with open("test_collection.txt", 'r') as f:
        article_bodies = f.readlines()
    
    for doc_number, body in enumerate(article_bodies):
        pre_processed_words = body.split(" ") # !!! this pre-processing step needs to be updated accordingly
        index = index_extender(pre_processed_words, index, doc_number)


def index_writer(inverted_index_dictionary):
    """
    input params:
    inverted_index_dictionary : dictionary
        index in the encoded dictionary form {word: [(doc_id_v_byte, position_v_byte)]}

    initiate word2byte hash
    open index handle
        for word, list in the index:
            find the current byte
            write the k,v to the file
            find the new byte after writing
            find the difference between new and old byte
            build tuple of (current byte, byte difference)
            store word2byte: {word, (current byte, byte difference)}

    return:
    index file
    hash table word2byte_location
    """
    return

def delta_decoder(delta_encoded_inverted_list):
    """
    input params:
    v_byte_encoded_inverted_list : dictionary
        one key being the word, and values a list with delta encoded doc_id and decoded positions

    return:
    inverted list in its original format {word: [(doc_id, position)]}
    """
    return

def v_byte_decoder(encoded_inverted_list):
    """
    input params:
    encoded_inverted_list : dictionary
        one key being the word, and values a list with v-byte encoded doc_id and positions

    return:
    inverted list in delta encoded format {word: [(doc_id_delta_encoded, position_decoded)]}
    """
    return

def retrieval(word_list, word2byte):
    """
    input params:
    word_list : list
        list of pre-processed words in the query
    word2byte : dictionary
        dictionary with collection vocabulary as keys and index byte start and size as value

    initialise mini index (this will eventually be returned)
    sets pointer to file handle
    for each word in the query: 
        finds the byte pointer and size
        retrieve the inverted list
        v byte decode the list
        delta decode the list
        add decoded list to mini index

    return:
    mini index in original format: dictionary of list of tuples {word: [(doc_id, position)]}
    """

    return

if __name__ == "__main__":
    index_builder()