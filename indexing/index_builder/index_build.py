import sys
import json
import ast

from datetime import datetime
from operator import sub
from itertools import starmap, islice

from database_population.db_connection import connect
from database_population.db_updater import add_row
from index_builder.helpers import Preprocessing

def index_extender(text_body, index, doc_number):

    for position, word in enumerate(text_body):

        if word in index:

            last_doc_number = index[word][1][-1][0]
            
            # only add the position to the position list of the existing document number entry
            if doc_number == last_doc_number: 
                index[word][1][-1][1].append(position + 1) 
            # add new doc number/position list to inverted list
            else:
                index[word][1].append([doc_number, [position + 1]])
                # increment document count of word
                index[word][0] += 1
        
        # build the initial list of doc/pos combos, no delta encoding on this iteration
        else:
            index[word] = [1, [[doc_number, [position + 1]]]]
    
    return index

def delta_encoder(index):
    encoded_index = {}

    for word in index:
        occurences, inverted_list = index[word]

        # calculates the delta values and rebuilds the inverted list with deltas
        deltas = starmap(
            lambda x, y: [x[0] - y[0], x[1]], 
            zip(inverted_list[1:], inverted_list)
        )
        encoded_inverted_list = [inverted_list[0], *deltas]

        encoded_index[word] = [occurences, encoded_inverted_list]
    return encoded_index

def date2doc_updater(date, doc_id, date2doc):
    if date in date2doc: 
        date2doc[date].append(doc_id)
    else:
        date2doc[date] = [doc_id]
    return date2doc

def json_writer(data, path):
    with open(path, 'w') as f:
        json.dump(data, f)
    return

def index_builder(content_file, 
                 stop_word_file_path,
                 database_config_path,
                 database_cert_path,
                 dict_size_path,
                 link_dict_path,
                 doc_size_path,
                 index_path,
                 date2doc_path):
    """
    return:
    index in the encoded dictionary form 
                        {word: [document_count, [ [doc_delta, [positions]], [doc_delta, [positions]], ... ]}
    """
    inverted_index = {}
    links_dict = {}
    sizes_dict = {}
    date2doc = {}

    connection, cursor = connect(database_config_path, database_cert_path)

    doc_id = 1

    with open(content_file, 'r') as f:
        next(f) # skip the header, delete for a file without header
        while doc_id < 1000:
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
                publish_date_object = datetime.strptime(publish_date.strip(' 00:00:00'), '%Y-%m-%d')
                title = title.replace('\'', '\'\'')
                content = body.replace('\'', '\'\'')
            except:
                print('Skipped a document')
                continue
            
            date2doc = date2doc_updater(publish_date, doc_id, date2doc)

            print("talking to db")
            # add row to the database with the new info
            add_row(doc_id, title, url, publish_date_object, content, cursor, connection)

            # prepare text data for indexing
            preprocessing = Preprocessing(stop_word_file_path)
            pre_processed_article = preprocessing.apply_preprocessing(full_text)

            # update size_dict
            content_length = len(pre_processed_article)
            sizes_dict[str(doc_id)] = int(content_length)

            # update links dict
            if len(links) > 0:
                links = [link.strip() for link in ast.literal_eval(links)]
                links_dict[str(doc_id)] = links
            
            time_before = datetime.now()
            # update index
            inverted_index = index_extender(pre_processed_article, inverted_index, int(doc_id))
            doc_id += 1
            indexing_time = datetime.now() - time_before
            print(indexing_time)
            print('-------------')

    # write links and doc sizes to file
    json_writer(links_dict, link_dict_path)
    json_writer(sizes_dict, doc_size_path)
    json_writer(date2doc, date2doc_path)

    # delta encode inverted index for index writing
    encoded_index = delta_encoder(inverted_index)
    json_writer(encoded_index, index_path)

    return encoded_index