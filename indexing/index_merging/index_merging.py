import json
import os

# with open("../output/index_and_index_hash/index_2.json") as f:
#     while True:
#         line = f.readline().strip('\n')
#         if not line:
#             break
#         term_dict = json.loads(line)
#         print(term_dict)

def index_merge(index1, index2, output_index):
    with open(index1, "r") as f1:
        with open(index2, "r") as f2:
            with open(output_index, "w") as f_out:
                line_f1 = json.loads(f1.readline())
                line_f2 = json.loads(f2.readline())

                while True:
                    term_f1 = list(line_f1.keys())[0]
                    term_f2 = list(line_f2.keys())[0]

                    # merge
                    if term_f1 == term_f2:
                        # merge the inverted lists
                        dict_to_write = {term_f1: []}
                        total_doc_count = line_f1[term_f1][0] + line_f2[term_f2][0]
                        total_inverted_list = {**line_f1[term_f1][1], **line_f2[term_f2][1]}
                        dict_to_write[term_f1].append(total_doc_count)
                        dict_to_write[term_f1].append(total_inverted_list)
                        
                        # write merged list to file
                        string_to_write = json.dumps(dict_to_write) + '\n'
                        
                        # read next line of both f1 and f2
                        print(f"{term_f1} and {term_f2}, so I'm updating both")
                        try:
                            line_f1 = json.loads(f1.readline())
                            line_f2 = json.loads(f2.readline())
                        except Exception:
                            print("finished merging")
                            break
                    
                    # write f1 to final index
                    if term_f1 < term_f2:
                        print(f"{term_f1} and {term_f2}, so I'm updating {term_f1}")

                        # write f1
                        string_to_write = json.dumps(line_f1) + '\n'
                    
                        # update f1
                        try:
                            line_f1 = json.loads(f1.readline())
                        except Exception:
                            print("finished merging")
                            break

                    # write f2 to final index
                    if term_f1 > term_f2:
                        print(f"{term_f1} and {term_f2}, so I'm updating {term_f2}")
                        
                        string_to_write = json.dumps(line_f2) + '\n'

                        # update f2
                        try:    
                            line_f2 = json.loads(f2.readline())
                        except Exception:
                            print("finished merging")
                            break

                    # write the appropriate string for the iteration
                    f_out.write(string_to_write)

if __name__ == "__main__":
    INDEX_PATH = "../output/index_and_index_hash/"

    INDEX1_PATH = os.path.join(INDEX_PATH, input(("index 1: ")))
    INDEX2_PATH = os.path.join(INDEX_PATH, input(("index 2: ")))
    INDEX_OUT_PATH = os.path.join(INDEX_PATH, "merged_index.json")

    index_merge(INDEX1_PATH, INDEX2_PATH, INDEX_OUT_PATH)