# input all documents and make an inverted index out of them
from collections import defaultdict

def make_positional_index(corpus: list[dict[str, str | list[str]]]): #-> dict[str, dict[str, int | list[tuple[int, int]]]]:
    positional_index = {}

    for document in corpus:
        doc_id = document["doc_id"]
        tokens = document["tokens"]
        local_positions = defaultdict(list) # eg: {"cotton" : [1,4,6,...], "men": [...], ...} 

        for position, token in enumerate(tokens, start=1):
            local_positions[token].append(position)

        for token, positions in local_positions.items():
            if token not in positional_index:
                positional_index[token] = {
                    "df": 0,
                    "postings": []
                }

            positional_index[token]["df"] += 1
            positional_index[token]["postings"].append(
                (doc_id, len(positions), positions)
            )

    return positional_index