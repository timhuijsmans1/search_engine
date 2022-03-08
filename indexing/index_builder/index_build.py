from __future__ import print_function
from sys import getsizeof, stderr
from itertools import chain
from collections import deque
try:
    from reprlib import repr
except ImportError:
    pass

import json
import ast
import signal
import time
import html
import os

from datetime import datetime
from operator import sub
from itertools import starmap, islice

from database_population.db_connection import connect
from database_population.db_updater import add_row
from index_builder.helpers import Preprocessing
from index_writer.index_writer import index_writer

def index_extender(text_body, index, doc_number):
    for position, word in enumerate(text_body):
        if word in index:
            if doc_number in index[word][1]:
                index[word][1][doc_number].append(position + 1)
            else:
                index[word][1][doc_number] = [position + 1]
                index[word][0] += 1
        
        else:
            index[word] = [1, {doc_number: [position + 1]}]

    return index

def index_extender_list(text_body, index, doc_number):

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

def total_size(o, handlers={}, verbose=False):
    
    dict_handler = lambda d: chain.from_iterable(d.items())
    all_handlers = {tuple: iter,
                    list: iter,
                    deque: iter,
                    dict: dict_handler,
                    set: iter,
                    frozenset: iter,
                   }
    all_handlers.update(handlers)     # user handlers take precedence
    seen = set()                      # track which object id's have already been seen
    default_size = getsizeof(0)       # estimate sizeof object without __sizeof__

    def sizeof(o):
        if id(o) in seen:       # do not double count the same object
            return 0
        seen.add(id(o))
        s = getsizeof(o, default_size)

        if verbose:
            print(s, type(o), repr(o), file=stderr)

        for typ, handler in all_handlers.items():
            if isinstance(o, typ):
                s += sum(map(sizeof, handler(o)))
                break
        return s

    return sizeof(o)

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

def partial_writer(inverted_index, index_path, partial_count):
    sorted_index = dict(sorted(inverted_index.items()))
    output_path = os.path.join(index_path, "index_" + str(partial_count) + ".json")
    index_writer(sorted_index, output_path)

def index_builder(content_file, 
                 stop_word_file_path,
                 database_config_path,
                 database_cert_path,
                 dict_size_path,
                 doc_size_path,
                 index_path,
                 date2doc_path):
    """
    return:
    index in the encoded dictionary form 
                        {word: [document_count, [ [doc_delta, [positions]], [doc_delta, [positions]], ... ]}
    """
    inverted_index = {}
    sizes_dict = {}
    date2doc = {}

    connection, cursor = connect(database_config_path, database_cert_path)

    doc_id = 1
    index_partial_count = 1

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
                publish_date_object = datetime.strptime(publish_date.strip(' 00:00:00'), '%Y%m%d')
                title = html.unescape(title.replace('\'', '\'\'')) # transform html entities to character
                content = body.replace('\'', '\'\'')
            except:
                print('Skipped a document because of the date format')
                continue
            
            date2doc = date2doc_updater(publish_date, doc_id, date2doc)
            
            added_row = add_row(doc_id,
                                title,
                                url,
                                publish_date_object,
                                content,
                                cursor,
                                connection
            )
            if added_row == False:
                try:
                    connection, cursor = connect(database_config_path, database_cert_path)
                except Exception:
                    print("cannot connect to the db, continue to next article and try again")
                continue

            # prepare text data for indexing
            preprocessing = Preprocessing(stop_word_file_path)
            pre_processed_article = preprocessing.apply_preprocessing(full_text)

            # update size_dict
            content_length = len(pre_processed_article)
            sizes_dict[str(doc_id)] = int(content_length)
        
            # update index
            inverted_index = index_extender(pre_processed_article, inverted_index, int(doc_id))

            doc_id += 1

            # if index starts to exceed size, write it to file and restart
            if doc_id % 10000 == 0:
                inverted_size = total_size(inverted_index) / 1000000
                date2_size = total_size(date2doc) / 1000000
                sizes_size = total_size(sizes_dict) / 1000000
                print(f"normal index size is {inverted_size} mb")
                print(f"date2 size is {date2_size} mb")
                print(f"sizes size is {sizes_size} mb")
                if inverted_size > 2000:
                    partial_writer(inverted_index, index_path, index_partial_count)
                    # delete the index copy
                    inverted_index = {}
                    index_partial_count += 1

    json_writer(sizes_dict, doc_size_path)
    json_writer(date2doc, date2doc_path)
    
    return