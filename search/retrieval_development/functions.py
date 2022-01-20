import re


def read_index_from_file(filepath):
    """
    Function to read the positional inverted index from file

    Format of the index: positional_index[word] = [number_of_appearances,
                                                    {document1: [position1, position2, ...],
                                                    document2: [position1, position2, ...]}
                                                    ]
    """
    number_pattern = r'[0-9]+' # regex
    inverted_index_dict = {}
    with open(filepath) as f:
        # is_new_term flags the first entry in the document which will represent a term
        # and its total number of appearances
        is_new_term = True
        lines = f.readlines()
        for line in lines:
            if line == '\n':
                # whitespace between every new term entrance in the file and a previous one
                is_new_term = True
                continue
            if is_new_term:
                line = line.split(':')
                term = line[0]
                occurences_in_file = int(line[1])
                inverted_index_dict[term] = [occurences_in_file]
                # Setting the flag to false to process the following lines which contain the positions of the term in
                # each document it appears in
                is_new_term = False
            else:
                document_entries = re.findall(number_pattern, line) # extracting ony number to get rid of ":" and new
                # line characters
                document_id = int(document_entries[0]) # first entry is document id
                positions = document_entries[1:] # rest of entries are positions in the doc
                positions = [int(position) for position in positions] # converting to integer
                inverted_index_dict[term].append({})
                inverted_index_dict[term][1][document_id] = positions
    return inverted_index_dict

if __name__ == '__main__':
    inverted_index = read_index_from_file("inverted_index.txt")
    queries = ["income tax reduction", "peace in the Middle East", "unemployment rate in UK",
               "industry in Scotland", "the industries of computers", "Microsoft Wdinows", "stock market in Japan",
               "the education with computers", "health industry", "campaigns of political parties"]



    test = 0