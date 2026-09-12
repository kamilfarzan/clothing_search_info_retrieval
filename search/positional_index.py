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

    # eg. {"cotton": {"df": 42, "postings": [("D001", 3, [1,2,3]), ("D004", 5, [5,6,8,11,21]), ...]}}
    return positional_index

#### ----
#### PHRASE SEARCH
#### ----

def lookup_positions(postings): # converting tuple to dict for quick lookup
    # eg. {"D001": [1,2,3], "D004": [5,6,8,11,21], ...}
    return {
        doc_id: positions for doc_id, tf, positions in postings
    }

def phrase_position_matching(positions_1, positions_2): # eg. "cotton shirt", use 2-pointers to match when cotton and shirt are in exact consecutive order
    i = j = 0

    while i < len(positions_1) and j < len(positions_2):
        if positions_2[j] == positions_1[i] + 1:
            return (positions_1[i], positions_2[j])

        elif positions_2[j] <= positions_1[i]:
            j += 1
        else:
            i += 1 

    return (-1, -1)

def phrase_search(query, positional_index, preprocess):
    print(query)
    terms = preprocess(query)

    if len(terms) != 2:
        raise ValueError("Use only two terms.")

    term1, term2 = terms

    if term1 not in positional_index or term2 not in positional_index:
        return []

    positions_1 = lookup_positions(positional_index[term1]["postings"])
    positions_2 = lookup_positions(positional_index[term2]["postings"])

    common_docs = set(positions_1.keys()) & set(positions_2.keys())


    results = []

    for document in sorted(common_docs):
        match_1, match_2 = phrase_position_matching(positions_1[document], positions_2[document])
        if (match_1, match_2) != (-1, -1):
            results.append({
                "doc_id": document, 
                "positions": {term1: match_1, term2: match_2}
            })

    return results

#### ----
#### PROXIMITY SEARCH
#### ----

def positions_within(positions_1, positions_2, within_k):
    i = j = 0

    while i < len(positions_1) and j < len(positions_2):
        difference = positions_2[j] - positions_1[i]

        if 0 < difference <= within_k:
            return (positions_1[i], positions_2[j])

        elif difference <= 0:
            j+=1
        else:
            i += 1

    return (-1, -1)

def proximity_search(term1, term2, within_k, positional_index, preprocess):
    term1 = preprocess(term1)[0]
    term2 = preprocess(term2)[0]

    if term1 not in positional_index or term2 not in positional_index:
        return []

    positions_1 = lookup_positions(positional_index[term1]["postings"])
    positions_2 = lookup_positions(positional_index[term2]["postings"])

    print(positions_1)
    print(positions_2)

    common_docs = set(positions_1.keys()) & set(positions_2.keys())


    results = []

    for document in sorted(common_docs):
        match_1, match_2 = positions_within(positions_1[document], positions_2[document], within_k)
        if (match_1, match_2) != (-1, -1):
            results.append({
                "doc_id": document, 
                "positions": {term1: match_1, term2: match_2}
            })
    
    return results