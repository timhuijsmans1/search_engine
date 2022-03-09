import vbcode

def delta_decoder(delta_list):
    current_doc_id = delta_list[0]
    doc_ids = [current_doc_id]
    for delta in delta_list[1:]:
        current_doc_id = delta + current_doc_id
        doc_ids.append(current_doc_id)

    return doc_ids

def decoder(encoded_index, query):
    mini_index = {}
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

    return mini_index