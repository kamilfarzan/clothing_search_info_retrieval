# let query be "men cotton winter"
from collections import Counter, defaultdict
import math

def build_document_vectors(inverted_index):
    # for each document, calculate term weights (lnc)
    document_vectors = defaultdict(dict)

    for term, data in inverted_index.items():
        for doc_id, term_freq in data["postings"]:
            weight = 1 + math.log10(term_freq)
            document_vectors[doc_id][term] = weight

    # document vectors look like:
    # ["D001"] : {"men": 1.45, "cotton": 1.33, ...}


    document_norms = {}

    for doc_id, vector in document_vectors.items():
        norm = math.sqrt(sum(w * w for w in vector.values()))
        document_norms[doc_id] = norm

    # document norms look like:
    # ["D001"]: 1.49

    return document_vectors, document_norms

def build_query_vector(tokens, inverted_index, N: int):
    # for the query, calculate term weights (ltc)
    tf_counts = Counter(tokens)
    query_vector = {}

    for term, freq in tf_counts.items():
        if term not in inverted_index:
            continue

        df = inverted_index[term]["df"]
        weight = (1 + math.log10(freq)) * math.log10(N / df)    # main point

        query_vector[term] = weight     # raw tf-idf-wt for each token (not normed)

    # query vector looks like:
    # {"men": 1.01, "cotton": 1.1}

    # norm part
    query_norm = math.sqrt(sum(w * w for w in query_vector.values())) 
    # query norm is just one float number

    return query_vector, query_norm     # we can divide later 

def search(query, inverted_index, document_vectors, document_norms, preprocess, N, k):
    tokens = preprocess(query)
    query_vector, query_norm = build_query_vector(tokens, inverted_index, N)
    scores = defaultdict(float)

    # dot product the vectors first (query * each doc)
    for term, query_weight in query_vector.items():
        for doc_id, _ in inverted_index[term]["postings"]:
            doc_weight = document_vectors[doc_id][term]
            scores[doc_id] += query_weight * doc_weight

    final_results = []

    for doc_id, dot_product in scores.items():
        doc_score = dot_product / (document_norms[doc_id] * query_norm)
        final_results.append((doc_id, doc_score))

    final_results.sort(key=lambda x: (-x[1], x[0]))

    return final_results[:k]