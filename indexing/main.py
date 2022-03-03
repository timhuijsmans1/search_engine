import json
import os

from index_builder.index_build import index_builder
from index_writer.index_writer import index_writer

if __name__ == "__main__":
    CONTENT_FILE = "data/article_data/ALL_gd_output_30Jan6Feb_content.tsv"
    STOP_WORD_FILE_PATH = "data/helper_data/englishST.txt"

    OUTPUT_LOCATION = 'output/index_and_index_hash'
    INDEX_OUTPUT = 'index.json'
    INDEX_HASH_OUTPUT = 'word2byte.json'
    DICTIONARY_SIZE_OUTPUT = 'dict_size.txt'
    DOC_SIZE_OUTPUT = 'doc_sizes.json'
    LINKS_OUTPUT = 'links.json'
    DATE2DOC_OUTPUT = 'date2doc.json'

    DATABASE_CONFIG_PATH = 'database_population/db.ini'
    DATABASE_CERT_PATH = 'database_population/certs'

    # this function builds the inverted index in dictionary form
    inverted_index_final = index_builder(CONTENT_FILE,
                                        STOP_WORD_FILE_PATH,
                                        DATABASE_CONFIG_PATH,
                                        DATABASE_CERT_PATH,
                                        os.path.join(OUTPUT_LOCATION, DICTIONARY_SIZE_OUTPUT),
                                        os.path.join(OUTPUT_LOCATION, LINKS_OUTPUT),
                                        os.path.join(OUTPUT_LOCATION, DOC_SIZE_OUTPUT),
                                        os.path.join(OUTPUT_LOCATION, INDEX_OUTPUT),
                                        os.path.join(OUTPUT_LOCATION, DATE2DOC_OUTPUT))
    
    # this function writes the index to memory and returns the byte offset hash
    # index_writer(inverted_index_final, 
    #                         os.path.join(OUTPUT_LOCATION, INDEX_OUTPUT), 
    #                         os.path.join(OUTPUT_LOCATION, INDEX_HASH_OUTPUT))

    
