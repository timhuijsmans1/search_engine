import json
import os

from index_builder.index_build import index_builder
from index_writer.index_writer import index_writer

if __name__ == "__main__":
    CONTENT_FILE = "data/article_data/Final.tsv"
    STOP_WORD_FILE_PATH = "data/helper_data/englishST.txt"

    OUTPUT_LOCATION = 'output/index_and_index_hash'
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
                                        os.path.join(OUTPUT_LOCATION, DOC_SIZE_OUTPUT),
                                        OUTPUT_LOCATION,
                                        os.path.join(OUTPUT_LOCATION, DATE2DOC_OUTPUT))

    
