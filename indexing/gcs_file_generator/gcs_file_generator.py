import json
import os
import sys
import gcsfs
from datetime import datetime


from google.cloud import storage

print("finished imports")

def converter(dict_string):
    term_dict = json.loads(dict_string)
    term = list(term_dict.keys())[0]
    print(term)
    doc_count, inverted_list = term_dict[term]
    doc_ids = inverted_list.keys()
    pos_lists = inverted_list.values()
    tfs = [len(pos_list) for pos_list in pos_lists]
    inverted_tf_list = dict(zip(doc_ids, tfs))
    dict_out = {term: [doc_count, inverted_tf_list]}
    dict_string_out = json.dumps(dict_out)

    return dict_string_out, term

def hasher_and_writer(index_path):
    client = storage.Client()
    bucket = client.get_bucket('django-test-344010.appspot.com')
    blob = bucket.get_blob("final_index_gcs.json")
    word2byte = {}
    with blob.open(mode='w') as blob_handle:
        count = 0
        with open(index_path, 'r') as index_handle: 
            byte_before = 0   
            while True:
                line = index_handle.readline().strip("\n")
                if not line:
                    break
                word = list(json.loads(line).keys())[0]
                print(word)
                blob_handle.write(line)
                byte_offset = len(line)
                end_byte = byte_before + byte_offset
                word2byte[word] = (byte_before, end_byte - 1)
                byte_before = end_byte
                count += 1

    with open("final_word2byte_gcs_django.json", 'w') as f:
        json.dump(word2byte, f)

    return word2byte

def hasher_and_writer_conversion(index_path):
    client = storage.Client()
    bucket = client.get_bucket('django-test-344010.appspot.com')
    blob = bucket.get_blob("final_index_tf_gcs.json")
    word2byte_tf = {}
    with blob.open(mode='w') as blob_handle:
        count = 0
        with open(index_path, 'r') as index_handle: 
            byte_before = 0   
            while True:
                line = index_handle.readline().strip("\n")
                if not line:
                    break
                converted_dict, word = converter(line)
                blob_handle.write(converted_dict)
                byte_offset = len(converted_dict)
                end_byte = byte_before + byte_offset
                word2byte_tf[word] = (byte_before, end_byte - 1)
                byte_before = end_byte
                count += 1

    with open("final_word2byte_tf_gcs_django.json", 'w') as f:
        json.dump(word2byte_tf, f)
    
    return word2byte_tf

def retrieval_test(word2byte, word2byte_tf, test_term):
    # retrieve non-tf
    client = storage.Client()
    bucket = client.get_bucket('django-test-344010.appspot.com')
    blob = bucket.get_blob("final_index_gcs.json")
    string_non_tf = json.loads(blob.download_as_string(start=word2byte[test_term][0], end=word2byte[test_term][1]).decode())

    # retrieve tf
    blob = bucket.get_blob("final_index_tf_gcs.json")
    string_tf = json.loads(blob.download_as_string(start=word2byte_tf[test_term][0], end=word2byte_tf[test_term][1]).decode())

    print("non-tf retrieved")
    print(string_non_tf)

    print("tf retrieved")
    print(string_tf)

    return

def manual_test(start_byte, end_byte):
    client = storage.Client()
    bucket = client.get_bucket('ttds2-338418.appspot.com')
    blob = bucket.get_blob("final_index_tf_gcs.json")
    string_non_tf = json.loads(blob.download_as_string(start=start_byte, end=end_byte).decode())
    print(string_non_tf)
    return

def line_read_test():
    fs = gcsfs.GCSFileSystem(project='django-test-344010')
    with fs.open('django-test-344010.appspot.com/line_test.txt', 'rb') as f:
        count = 1
        while True:
            line = f.readline()
            print(count, line)
            if not line:
                print(count, "I broke")
                break
            count += 1
            

if __name__ == "__main__":
    INDEX_PATH = "../output/index_and_index_hash/index_1.json"
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="django-test-344010-092a23419933.json"
    # word2byte_out = hasher_and_writer(INDEX_PATH)
    # word2byte_tf_out = hasher_and_writer_conversion(INDEX_PATH)
    line_read_test()
    # retrieval_test(word2byte_out, word2byte_tf_out, 'data')
    # manual_test(34712666, 34822414)