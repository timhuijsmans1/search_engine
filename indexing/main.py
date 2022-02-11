import json
import os

from index_builder.index_build import index_builder
from index_writer.index_writer import index_writer
from index_retrieval.index_retrieval import retrieval

if __name__ == "__main__":
    CONTENT_FILE = "data/article_data/5_article_test.tsv"
    STOP_WORD_FILE_PATH = "data/helper_data/englishST.txt"

    OUTPUT_LOCATION = 'output/index_and_index_hash'
    INDEX_OUTPUT = 'index.json'
    INDEX_HASH_OUTPUT = 'word2byte.json'
    DICTIONARY_SIZE_OUTPUT = 'dict_size.txt'

    DATABASE_CONFIG_PATH = 'database_population/db.ini'
    DATABASE_CERT_PATH = 'database_population/certs'

    # this function builds the inverted index in dictionary form
    inverted_index_final = index_builder(CONTENT_FILE, 
                                        STOP_WORD_FILE_PATH, 
                                        DATABASE_CONFIG_PATH, 
                                        DATABASE_CERT_PATH,
                                        os.path.join(OUTPUT_LOCATION, DICTIONARY_SIZE_OUTPUT))
    

    # this function writes the index to memory and returns the byte offset hash
    index_writer(inverted_index_final, 
                            os.path.join(OUTPUT_LOCATION, INDEX_OUTPUT), 
                            os.path.join(OUTPUT_LOCATION, INDEX_HASH_OUTPUT))

    
    # this part can be used to retrieve the decoded mini index for a query
    # # first, load word2byte into memory
    # with open(os.path.join(OUTPUT_LOCATION, INDEX_HASH_OUTPUT), 'r') as f:
    #     word2byte = json.load(f)

    # # second, load the relevant bytes into file and decode the index
    # sub_index = retrieval(["world"], os.path.join(OUTPUT_LOCATION, INDEX_OUTPUT), word2byte)

    
