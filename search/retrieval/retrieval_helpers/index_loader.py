import json

def load_mini_index(word_list, index_path, word2byte):
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

    with open(index_path, 'r') as f:

        # only load and decode the index of each word once
        for word in set(word_list):
            try: # if query word is in our vocabulary
                start_byte = word2byte[word][0]
                bytes_to_read = word2byte[word][1]

                # find the bytes where we need to start reading
                f.seek(start_byte)
                inverted_list = f.read(bytes_to_read)

                # add inverted list to the index we want to retrieve
                inverted_list_dict = json.loads(inverted_list)
                mini_index = {**mini_index, **inverted_list_dict}
                
            except:
                pass # if query word is not in our vocabulary
    
    return mini_index