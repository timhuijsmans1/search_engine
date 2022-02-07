import json

def index_extender(text_body, index, doc_number):
    """
    input params:
    text_body : list
        list of all the pre-processed tokens in a text body
    index : dictionary
        the current index with lists delta and v-byte encoded

    return:
    extended index in the following format: {word: [document_count, [ [doc_delta, [positions]], [doc_delta, [positions]], ... ]}
    """

    for position, word in enumerate(text_body):

        if word in index:

            # sums deltas to find the most recently added doc number of the current word.
            last_doc_number = sum([doc_tuple[0] for doc_tuple in index[word][1]])
            delta = doc_number - last_doc_number

            # only add the position to the position list of the existing document number entry
            if doc_number == last_doc_number: 
                index[word][1][-1][1].append(position + 1) 
            # add new doc number/position list to inverted list
            else:
                index[word][1].append([delta, [position + 1]])
                index[word][0] += 1
        # build the initial list of doc/pos combos, no delta encoding on this iteration
        else:
            index[word] = [1, [[doc_number, [position + 1]]]]

    return index

def index_builder():
    """
    return:
    index in the encoded dictionary form {word: [document_count, [ [doc_delta, [positions]], [doc_delta, [positions]], ... ]}
    """
    index = {}

    # !!! manually getting some text bodys for testing, update this to url retrieval
    with open("test_collection_2.txt", 'r') as f:
        article_bodies = f.readlines()
    
    # extend the index for every document that is added
    for doc_number, body in enumerate(article_bodies):
        pre_processed_words = [word.strip('\n') for word in body.split(" ")] # !!! this pre-processing step needs to be updated accordingly
        index = index_extender(pre_processed_words, index, doc_number + 1)
    
    return index

def index_writer(index):
    """
    input params:
    inverted_index_dictionary : dictionary
        index in the encoded dictionary form {word: [document_count, [ [doc_delta, [positions]], [doc_delta, [positions]], ... ]}

    return:
    index file
    hash table word2byte_location
    """
    word2bytes = {}
    with open("index.json", 'w') as f:
        for word in index:
            start_byte = f.tell()

            # write k,v to file
            dict_to_write = {word: index[word]}
            string = json.dumps(dict_to_write)
            f.write(string)
            end_byte = f.tell()
            bytes_to_read = end_byte - start_byte
            byte_values = (start_byte, bytes_to_read)
            word2bytes[word] = byte_values

    return word2bytes

def delta_decoder(delta_encoded_inverted_list, word):
    """
    input params:
    v_byte_encoded_inverted_list : dictionary
        one key being the word, and values a list with delta encoded doc_id and decoded positions

    return:
    inverted list in its original format {word: [document_count, [[doc_number, [positions]]]}
    """
    dict_out = {word: {}}

    doc_count, doc_numbers = delta_encoded_inverted_list[word]

    # add the first doc number manually
    doc_number, positions = doc_numbers[0]
    dict_out[word][doc_number] = positions

    # loop over all but the first doc_numbers, first is not encoded
    for i in range(1, len(doc_numbers)):
        doc_number = sum([doc_tuple[0] for doc_tuple in doc_numbers[:i + 1]]) # calculate the doc number for each delta
        positions = doc_numbers[i][1]
        dict_out[word][doc_number] = positions

    return dict_out

def retrieval(word_list, word2byte, index_path):
    """
    input params:
    word_list : list
        list of pre-processed words in the query
    word2byte : dictionary
        dictionary with collection vocabulary as keys and index byte start and size as value

    return:
    mini index in original format: dictionary of list of tuples {word: [document_count, [ [doc_number, [positions]], [doc_number, [positions]], ... ]}
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

if __name__ == "__main__":
    INDEX_PATH = "index.json"

    index = index_builder()
    word2byte = index_writer(index)
    retrieval(['hello', 'edinburgh'], word2byte, INDEX_PATH)