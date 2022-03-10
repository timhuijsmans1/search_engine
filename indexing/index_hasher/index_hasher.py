from __future__ import print_function
from sys import getsizeof, stderr
from itertools import chain
from collections import deque
try:
    from reprlib import repr
except ImportError:
    pass

import json
import os

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

def index_hasher(index_path, word2byte_out_path):

    word2byte = {}
    with open(index_path, "r") as f:
        while True:
            start_byte = f.tell()
            line_string = f.readline()
            end_byte = f.tell()
            byte_diff = end_byte - start_byte
            if line_string:
                term_dict = json.loads(line_string)
                term = list(term_dict.keys())[0]
                word2byte[term] = (start_byte, byte_diff)
            else:
                break
    
    print(total_size(word2byte) / 1000000)

    with open(word2byte_out_path, 'w') as f:
        string_out = json.dump(word2byte, f)

    return

    
if __name__ == "__main__":
    INDEX_PATH = "../output/index_and_index_hash/"

    HASH_NAME = "word2byte.json"
    INDEX_NAME = "index_1.json"

    index_hasher(os.path.join(INDEX_PATH, INDEX_NAME), os.path.join(INDEX_PATH, HASH_NAME))