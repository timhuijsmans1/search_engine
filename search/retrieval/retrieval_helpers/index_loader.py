import json
import ujson
import line_profiler
import atexit
from retrieval.retrieval_helpers.helpers import seperate_mix

from google.cloud import storage

profile = line_profiler.LineProfiler()
atexit.register(profile.print_stats)

@profile
def gcs_mini_index(word_list, word2byte, word2byte_tf):
    """
    input params:
    word_list : list
        list of pre-processed words in the query
    word2byte : dictionary
        dictionary with collection vocabulary as keys and index byte start and size as value

    return:
    mini index in original format, only containing those inverted lists that are relevant to the query: 
                        {word: [document_count, [ [doc_number, [positions]], [doc_number, [positions]], ... ]}
    """
    mini_index = {}
    singles_updated = []

    singles, phrases = seperate_mix(word_list)
    for term in singles:
        singles_updated.append([term])

    client = storage.Client()
    bucket = client.get_bucket('ttds2-338418.appspot.com')

    if singles_updated:
        blob = bucket.get_blob("final_index_tf_gcs.json")
        # only load and decode the index of each word once
        for word in set(sum(singles_updated, [])):
            try:  # if query word is in our vocabulary
                start_byte = word2byte_tf[word][0]
                end_byte = word2byte_tf[word][1]
                
                json_string = blob.download_as_string(start=start_byte, end=end_byte).decode()

                # add inverted list to the index we want to retrieve
                inverted_list_dict = ujson.loads(json_string)
                mini_index = {**mini_index, **inverted_list_dict}

            except:
                pass # if query word is not in our vocabulary

    if phrases:
        blob = bucket.get_blob("final_index_gcs.json")
        # only load and decode the index of each word once
        for word in set(sum(phrases, [])):
            try:  # if query word is in our vocabulary
                start_byte = word2byte[word][0]
                end_byte = word2byte[word][1]

                json_string = blob.download_as_string(start=start_byte, end=end_byte).decode()

                # add inverted list to the index we want to retrieve
                inverted_list_dict = ujson.loads(json_string)
                mini_index = {**mini_index, **inverted_list_dict}

            except:
                pass  # if query word is not in our vocabulary

    return mini_index

def load_mini_index(word_list, index_path_1, index_path_2, word2byte_tf, word2byte):
    """
    input params:
    word_list : list
        list of pre-processed words in the query
    word2byte : dictionary
        dictionary with collection vocabulary as keys and index byte start and size as value

    return:
    mini index in original format, only containing those inverted lists that are relevant to the query: 
                        {word: [document_count, [ [doc_number, [positions]], [doc_number, [positions]], ... ]}
    """
    mini_index = {}
    singles_updated = []

    singles, phrases = seperate_mix(word_list)
    for term in singles:
        singles_updated.append([term])

    if singles_updated:
        with open(index_path_1, 'r') as f:
            # only load and decode the index of each word once
            for word in set(sum(singles_updated, [])):
                try:  # if query word is in our vocabulary
                    start_byte = word2byte_tf[word][0]
                    bytes_to_read = word2byte_tf[word][1]

                    # find the bytes where we need to start reading
                    f.seek(start_byte)
                    inverted_list = f.read(bytes_to_read)

                    # add inverted list to the index we want to retrieve
                    inverted_list_dict = ujson.loads(inverted_list)
                    mini_index = {**mini_index, **inverted_list_dict}

                except:
                    pass # if query word is not in our vocabulary

    if phrases:
        with open(index_path_2, 'r') as f:
            # only load and decode the index of each word once
            for word in set(sum(phrases, [])):
                try:  # if query word is in our vocabulary
                    start_byte = word2byte[word][0]
                    bytes_to_read = word2byte[word][1]

                    # find the bytes where we need to start reading
                    f.seek(start_byte)
                    inverted_list = f.read(bytes_to_read)

                    # add inverted list to the index we want to retrieve
                    inverted_list_dict = ujson.loads(inverted_list)
                    mini_index = {**mini_index, **inverted_list_dict}

                except:
                    pass  # if query word is not in our vocabulary

    return mini_index