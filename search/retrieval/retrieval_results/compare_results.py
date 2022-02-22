def read_in_file(filepath):
    documents_retrieved = []
    with open(filepath) as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if i == 0:
                line = line.rstrip()
                query = line
            else:
                line = line.rstrip()  # remove new line character
                doc_id = int(line)
                documents_retrieved.append(doc_id)
        return documents_retrieved, query


def find_how_many_in_same_position(bm_results, lm_results, results_filename, query):
    same_position_count = 0
    with open(results_filename, 'a') as f:
        f.write(query)
        f.write("\n")
        for i in range(len(bm_results)):
            if bm_results[i] == lm_results[i]:
                same_position_count += 1
                f.write("Elements in position %d are the same\n" % (i+1))
        f.write("Found %d elements in the same position\n" % same_position_count)


def find_how_many_are_retrieved_by_both(bm_results, lm_results, results_filename):
    bm_results = set(bm_results)  # converting to set to use intersection function
    intersection_results = bm_results.intersection(lm_results)
    with open(results_filename, 'a') as f:
        f.write("%d elements in the lists are the same, regardless of position\n" % len(intersection_results))
        f.write("\n")



if __name__ == '__main__':
    bm_results, bm_query = read_in_file("bm25 stock buy.txt")
    lm_results, lm_query = read_in_file("lm stock buy.txt")
    results_filename = "comparison_results.txt"
    find_how_many_in_same_position(bm_results, lm_results, results_filename, bm_query)
    find_how_many_are_retrieved_by_both(bm_results, lm_results, results_filename)
    stop = 0