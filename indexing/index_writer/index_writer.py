import json

def index_writer(index, index_path):
    """
    input params:
    inverted_index_dictionary : dictionary
        index in the encoded dictionary form 
                                {word: [document_count, [ [doc_delta, [positions]], [doc_delta, [positions]], ... ]}

    return:
    index file
    hash table word2byte_location
    """

    # writes the index to file and tracks the byte offset
    with open(index_path, 'w') as f:
        for word in index:

            # write k,v to file
            dict_to_write = {word: index[word]}
            string = json.dumps(dict_to_write) + '\n'
            f.write(string)

    return