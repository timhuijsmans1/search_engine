import json

def index_writer(index, index_path, word2byte_path):
    """
    input params:
    inverted_index_dictionary : dictionary
        index in the encoded dictionary form 
                                {word: [document_count, [ [doc_delta, [positions]], [doc_delta, [positions]], ... ]}

    return:
    index file
    hash table word2byte_location
    """
    word2bytes = {}

    # writes the index to file and tracks the byte offset
    with open(index_path, 'w') as f:
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

    # writes the byte offsets to file
    with open(word2byte_path, 'w') as f:
        json.dump(word2bytes, f)

    return