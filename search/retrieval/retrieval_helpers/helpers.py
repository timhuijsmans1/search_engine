def helper_example():
    # do something
    return None

def read_text_file(filepath):
    with open(filepath) as f:
        lines = f.readlines()
        return lines