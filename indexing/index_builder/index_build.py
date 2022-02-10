from datetime import datetime

from database_population.db_connection import connect
from database_population.db_updater import add_row
from index_builder.helpers import Preprocessing

def index_extender(text_body, index, doc_number):
    """
    input params:
    text_body : list
        list of all the pre-processed tokens in a text body
    index : dictionary
        the current index with lists delta and v-byte encoded

    return:
    extended index in the following format: 
                        {word: [document_count, [ [doc_delta, [positions]], [doc_delta, [positions]], ... ]}
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

def index_builder(content_file, stop_word_file_path, database_config_path, database_cert_path):
    """
    return:
    index in the encoded dictionary form 
                        {word: [document_count, [ [doc_delta, [positions]], [doc_delta, [positions]], ... ]}
    """
    inverted_index = {}

    connection, cursor = connect(database_config_path, database_cert_path)

    # @ part 4 of word doc
    # input = csv with doc_id, title, url, date
    with open(content_file, 'r') as f:
        while True:
            line = f.readline().strip('\n')
            if not line:
                break

            doc_id, title, body, url, publish_date = line.split('\t')
            publish_date = datetime.strptime(publish_date, '%Y-%m-%d')
            add_row(int(doc_id), title, body, url, publish_date, cursor, connection)

            preprocessing = Preprocessing(stop_word_file_path)
            pre_processed_article = preprocessing.apply_preprocessing(body)

            inverted_index = index_extender(pre_processed_article, inverted_index, int(doc_id))

    return inverted_index