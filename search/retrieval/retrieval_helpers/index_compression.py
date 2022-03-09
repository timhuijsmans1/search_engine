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
                bytestream = compressor(doc2pos, doc_count)
                encoded_index[term] = bytestream
                count += 1

    return encoded_index

    