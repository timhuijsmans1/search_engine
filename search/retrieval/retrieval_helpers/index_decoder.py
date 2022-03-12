import vbcode
import line_profiler
import atexit

profile = line_profiler.LineProfiler()
atexit.register(profile.print_stats)

def delta_decoder(delta_list):
    current_doc_id = delta_list[0]
    doc_ids = [current_doc_id]
    for delta in delta_list[1:]:
        current_doc_id = delta + current_doc_id
        doc_ids.append(current_doc_id)

    return doc_ids

@profile
def decoder(encoded_index, query):
    mini_index = {}
    for word in set(sum(query, [])):
        encoded_list = encoded_index.get(word)
        if encoded_list:
            inverted_list = vbcode.decode(encoded_list)
            
            doc_count = inverted_list[0]
            docs_and_tf = inverted_list[1:]

            # even elements of the list are the deltas and odd elements are tf's
            deltas = docs_and_tf[0::2]
            doc_ids = delta_decoder(deltas)
            term_frequencies = docs_and_tf[1::2]
            
            # turn the list of alternating doc_id and tf into a dict
            docs2tf = dict(zip(doc_ids, term_frequencies))

            mini_index[word] = [doc_count, docs2tf]

    return mini_index