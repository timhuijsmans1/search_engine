from __future__ import print_function

import vbcode
import sys
import datetime
import json

from sys import getsizeof, stderr
from itertools import chain, islice, starmap
from collections import deque
from operator import sub
try:
    from reprlib import repr
except ImportError:
    pass

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

def compressor(doc2pos, doc_count):
    # split inverted list
    doc_ids, positions = zip(*doc2pos.items())
    term_frequencies = [len(position_list) for position_list in positions]
    doc_ids = [int(doc_id) for doc_id in doc_ids]
    # delta encoding of the list of document ids
    deltas = [doc_ids[0], *starmap(sub, zip(islice(doc_ids, 1, None), doc_ids))]

    inverted_list = []
    for i, delta in enumerate(deltas):
        inverted_list.append(delta)
        inverted_list.append(term_frequencies[i])

    inverted_list = [doc_count] + inverted_list

    inverted_list_bytestream = vbcode.encode(inverted_list)

    return inverted_list_bytestream

def index_compressor(index_path):
    encoded_index = {}
    count = 0
    with open(index_path, 'r') as f:
        while True: 
            line = f.readline()
            if not line:
                break
            else:
                index_line = json.loads(line)
                term = list(index_line.keys())[0]
                doc_count, doc2pos = index_line[term]
                if count == 2:
                    print(term, len(doc2pos.keys()))
                bytestream = compressor(doc2pos, doc_count)
                encoded_index[term] = bytestream
                count += 1
    
    print(total_size(encoded_index))
    print(count)

    return encoded_index

def delta_decoder(delta_list):
    current_doc_id = delta_list[0]
    doc_ids = [current_doc_id]
    for delta in delta_list[1:]:
        current_doc_id = delta + current_doc_id
        doc_ids.append(current_doc_id)

    return doc_ids


def decoder(encoded_index, query):
    mini_index = {}
    start_time = datetime.datetime.now()
    for word in set(query):
        encoded_list = encoded_index.get(word)
        if encoded_list:
            inverted_list = vbcode.decode(encoded_list)
            
            # split up doc_count and the doc_id, tf part of the inverted list
            doc_count = inverted_list[0]
            docs_and_tf = inverted_list[1:]

            deltas = docs_and_tf[0::2]
            doc_ids = delta_decoder(deltas)
            term_frequencies = docs_and_tf[1::2]
            
            # turn the list of alternating doc_id and tf into a map
            docs2tf = dict(zip(doc_ids, term_frequencies))

            mini_index[word] = [doc_count, docs2tf]
    
    print(f"decoding of the query {query} took {datetime.datetime.now() - start_time}")

    return mini_index

def json_writer(compressed_index, path):
    with open(path, "w") as f:
        json.dump(compressed_index, f)
    return

if __name__ == "__main__":
    INDEX_PATH = "../output/index_and_index_hash/index_1.json"
    COMPRESSED_INDEX_PATH = "../output/index_and_index_hash/compressed_index.json"
    index = index_compressor(INDEX_PATH)
    print(index)
    json_writer(index, COMPRESSED_INDEX_PATH)

    