# input all documents and make an inverted index out of them
from collections import Counter

def make_inverted_index(corpus: list[dict[str, str | list[str]]]) -> dict[str, dict[str, int | list[tuple[int, int]]]]:
    inverted_index = {}

    for document in corpus:
        doc_id = document["doc_id"]
        tokens = document["tokens"]

        # count term freq for all tokens; eg. [('men', 2),('tshirt', 3) , ...]
        term_frequencies = Counter(tokens)

        for token, freq in term_frequencies.items():
            if token not in inverted_index:
                inverted_index[token] = {"df": 0, "postings": []}

            inverted_index[token]["df"] += 1
            inverted_index[token]["postings"].append((doc_id, freq))

    return inverted_index

    # example of invered index:
    # {
    #     'cotton': {
    #         "df": 25,
    #         "postings": [(1, 3), (2, 4)]
    #     }
    # }

        # for token in document["tokens"]:
            # if not inverted_index.get(token, 0):
            #     inverted_index[token] = {}
            #     inverted_index[token]["df"] = 1
            #     inverted_index[token]["postings"] = [(document["doc_id"], document["tokens"].count(token))]
            # else:
            #     inverted_index[token]["df"] += 1
            #     inverted_index[token]["postings"] += [(document["doc_id"], document["tokens"].count(token))]
