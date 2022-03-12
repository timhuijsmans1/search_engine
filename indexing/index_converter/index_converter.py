import json
import orjson
import ujson
import os
import timeit

def index_converter(index_path, index_out_path, word2byte_out_path):
    count = 1
    word2byte = {}
    with open(index_out_path, 'w') as f_index_out:
        with open(index_path, "r") as f_index_in:
            while True:
                # get bytes for byte offset map
                dict_string = f_index_in.readline()
                if not dict_string:
                    break

                # read string and calculate tfs
                term_dict = json.loads(dict_string)
                term = list(term_dict.keys())[0]
                doc_count, inverted_list = term_dict[term]
                doc_ids = inverted_list.keys()
                pos_lists = inverted_list.values()
                tfs = [len(pos_list) for pos_list in pos_lists]
                inverted_tf_list = dict(zip(doc_ids, tfs))
                dict_out = {term: [doc_count, inverted_tf_list]}
                count += 1

                # write the inverted dict to index json
                start_byte = f_index_out.tell()
                string_to_write = json.dumps(dict_out)
                f_index_out.write(string_to_write)
                byte_difference = f_index_out.tell() - start_byte
                word2byte[term] = (start_byte, byte_difference)

                print(term)
    
    # write the word2byte to disk
    with open(word2byte_out_path, 'w') as f:
        json.dump(word2byte, f)
    
    return

def word2byte_reader(word2byte_path):
    with open(word2byte_path, 'r') as f:
        word2byte = json.load(f)

    return word2byte

def decompression_performance_test_u():
    
    # code to check performance of
    mini_index = {}
    with open(os.path.join(OUTPUT_PATH, INDEX_OUT_FILE), 'r') as f:

        # only load and decode the index of each word once
        for word in set(sum(word_list, [])):

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
                pass # if query word is not in our vocabulary

def decompression_performance_test_or():
    
    # code to check performance of
    mini_index = {}
    with open(os.path.join(OUTPUT_PATH, INDEX_OUT_FILE), 'r') as f:

        # only load and decode the index of each word once
        for word in set(sum(word_list, [])):

            try:  # if query word is in our vocabulary
                start_byte = word2byte[word][0]
                bytes_to_read = word2byte[word][1]

                # find the bytes where we need to start reading
                f.seek(start_byte)
                inverted_list = f.read(bytes_to_read)

                # add inverted list to the index we want to retrieve
                inverted_list_dict = orjson.loads(inverted_list)
                mini_index = {**mini_index, **inverted_list_dict}
                
            except:
                pass # if query word is not in our vocabulary


if __name__ == "__main__":
    OUTPUT_PATH = "../output/index_and_index_hash"
    INDEX_FILE = "final_index.json"
    INDEX_OUT_FILE = "final_index_tf.json"
    WORD2BYTE_OUT_FILE = "word2byte_tf.json"

    # This code takes 15 minutes, only run to convert the index
    # index_converter(os.path.join(OUTPUT_PATH, INDEX_FILE),
    #                 os.path.join(OUTPUT_PATH, INDEX_OUT_FILE),
    #                 os.path.join(OUTPUT_PATH, WORD2BYTE_OUT_FILE)
    # )
    word2byte = word2byte_reader(os.path.join(OUTPUT_PATH, WORD2BYTE_OUT_FILE))
    word_list = [["stock"], ["price"], ["facebook"], ["0"], ["1"]]

    loops = 1000
    result = timeit.timeit('decompression_performance_test_or()', globals=globals(), number=loops)
    print("or", result/loops)
    result = timeit.timeit('decompression_performance_test_u()', globals=globals(), number=loops)
    print("u", result/loops)



    
