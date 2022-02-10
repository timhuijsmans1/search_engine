import json

def delta_decoder(delta_encoded_inverted_list, word):
    """
    input params:
    v_byte_encoded_inverted_list : dictionary
        one key being the word, and values a list with delta encoded doc_id and decoded positions

    return:
    inverted list in its original format {word: [document_count, [[doc_number, [positions]]]}
    """

    doc_count, doc_numbers = delta_encoded_inverted_list[word]

    dict_out = {word: [doc_count, {}]}

    # add the first doc number manually
    doc_number, positions = doc_numbers[0]
    dict_out[word][1][doc_number] = positions

    # loop over all but the first doc_numbers, first is not encoded
    for i in range(1, len(doc_numbers)):
        doc_number = sum([doc_tuple[0] for doc_tuple in doc_numbers[:i + 1]]) # calculate the doc number for each delta
        positions = doc_numbers[i][1]
        dict_out[word][1][doc_number] = positions
    return dict_out

def retrieval(word_list, index_path, word2byte):
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
        for word in word_list:
            try: # if query word is in our vocabulary
                start_byte = word2byte[word][0]
                bytes_to_read = word2byte[word][1]

                # find the bytes where we need to start reading
                f.seek(start_byte)
                inverted_list = f.read(bytes_to_read)

                # add inverted list to the index we want to retrieve
                inverted_list_dict = json.loads(inverted_list)
                decoded_inverted_list = delta_decoder(inverted_list_dict, word)
                mini_index = {**mini_index, **decoded_inverted_list}
                
            except:
                pass # if query word is not in our vocabulary
    
    return mini_index