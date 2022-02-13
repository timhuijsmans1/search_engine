import sys
import json
import ast

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

        if index.get(word):

            # sums deltas to find the most recently added doc number of the current word.
            last_doc_number = sum([doc_tuple[0] for doc_tuple in index[word][1]])
            delta = doc_number - last_doc_number

            # only add the position to the position list of the existing document number entry
            if doc_number == last_doc_number: 
                index[word][1][-1][1].append(position + 1) 
            # add new doc number/position list to inverted list
            else:
                index[word][1].append([delta, [position + 1]])
                # increment document count of word
                index[word][0] += 1
        # build the initial list of doc/pos combos, no delta encoding on this iteration
        else:
            index[word] = [1, [[doc_number, [position + 1]]]]

    return index

def index_builder(content_file, 
                 stop_word_file_path,
                 database_config_path,
                 database_cert_path,
                 dict_size_path,
                 link_dict_path,
                 doc_size_path):
    """
    return:
    index in the encoded dictionary form 
                        {word: [document_count, [ [doc_delta, [positions]], [doc_delta, [positions]], ... ]}
    """
    inverted_index = {}
    links_dict = {}
    sizes_dict = {}

    connection, cursor = connect(database_config_path, database_cert_path)

    doc_id = 1

    # @ part 4 of word doc
    # input = tsv with doc_id \t title \t body \t url \t date
    with open(content_file, 'r') as f:
        next(f) # skip the header, delete for a file without header
        while True:
            print(doc_id)

            line = f.readline().strip('\n')
            if not line:
                break
            
            # extract line info
            title, url, publish_date, body, content_length, links = line.split('\t')
            full_text = title + ' ' +  body

            # skip articles that can not be loaded into the db
            if len(title) >= 1000 or len(url) >= 1000:
                continue

            # whenever the date is provided in the wrong format, skip the iteration
            try:
                # prepare data types for adding to db
                publish_date = datetime.strptime(publish_date.strip(' 00:00:00'), '%Y-%m-%d')
                title = title.replace('\'', '\'\'')
            except:
                print('Skipped a document')
                continue
            
            # add row to the database with the new info
            add_row(doc_id, title, url, publish_date, cursor, connection)

            preprocessing = Preprocessing(stop_word_file_path)
            pre_processed_article = preprocessing.apply_preprocessing(full_text)

            # update size_dict
            content_length = len(pre_processed_article)
            sizes_dict[str(doc_id)] = content_length

            # update links dict
            if len(links) > 0:
                links = [link.strip() for link in ast.literal_eval(links)]
                links_dict[str(doc_id)] = links

            # update index
            inverted_index = index_extender(pre_processed_article, inverted_index, int(doc_id))
            doc_id += 1

    with open(dict_size_path, 'w') as f:
        f.write(f'size of inverted index dict: {str(sys.getsizeof(inverted_index))} bytes\n')
        f.write(f'size of content length dict: {str(sys.getsizeof(sizes_dict))} bytes\n')
        f.write(f'size of link dict: {str(sys.getsizeof(links_dict))} bytes')

    with open(link_dict_path, 'w') as f:
        json.dump(links_dict, f)

    with open(doc_size_path, 'w') as f:
        json.dump(sizes_dict, f)

    return inverted_index