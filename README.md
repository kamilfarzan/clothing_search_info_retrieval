# clothing_search
## assignment for information retrieval

run fastAPI setup:

```bash
uv run uvicorn app:app --reload
```

### corpus:
imported from `search/loader.py`. 
there are 100 documents in the corpus, each with fields: DOCID, CATEGORY, TITLE & TEXT.

`document_blocks` are made using regex, and its constituent fields are also search using regex.

each field from the corpus is stored as a key, value pair in a document object, a raw entry of each complete unedited document is also stored. this object is then appended to the `docs` list and returned as the loaded corpus.


### preprocessing:
imported from `search/preprocess.py`.
preprocess of any text input does the following in order:
-> lowercases the `text`
-> removes any punctuation and extra white space, leaves alphanumerics and underscore
-> tokenizes the words (`word_tokenize` from `nltk`)
-> removes the stopwords from the `tokens` (standard nltk english stopwords, removes common words like the, is, and, of; this standard stopword set is used throughout the entire codebase)
-> stems the `filtered_tokens` (`PorterStemmer` from `nltk.stem`)

after this, return the `stemmed_tokens`.


### make inverted index:
imported from `search/inverted_index.py`
take in the corpus dictionary, which includes tokens now from preprocessing.
for each document in the corpus:
-> find the term frequencies (eg. [('men', 2),('tshirt', 3) , ...])
-> for each term in term_freqs:
->-> increment df, and add to `postings` list with `(doc_id, freq)`

this gives us the inverted index, where we have: `term -> df -> postings`


### vector space model:
imported from `search/vsm.py`:
(before we go for search, make document vectors and their norm values)
take input of query at endpoint `/search?query=` (can also add k as parameter for top k values)

preprocess query to tokens, and make the `query_vector` and `query_norm`
for each `term` in query_vector:
-> for eahc `doc_id` where these terms are (from inverted index)
->-> multiply the `doc_weight` and `query_weight` from the two vectors and store it in scores by `doc_id` as key (this is the dot product)

for final result for each doc, (normalization), divide the dot products by their `document_norms` and `query_norm`
append this final result to 2d array `final_results`, in the format `(doc_id, doc_score)`

sort this by decreasing `doc_score`, break ties by increasing `doc_id`
there is also an edge case here.
if a query term appears in all documents (df = N = 100), then log10(100/100) = log10(1) = 0,
so query_vector has zero weights, causing query_norm = 0.0  

return top `k` results (default k = 10)


### positional index:
imported from `search/positional_index.py`
similar to inverted index, we took corpus dictionary and output: `term -> df -> postings` but this time:
we have an extra entry in postings, so it looks like: `doc_id, tf, [...positions]`
this positions list is simply made from `enumerate(tokens, start=1)`, which gives us position for each token

(limitations: we are performing this positional indexing on tokens, not the original text, so if someone searches `cotton WITHIN/1 shirt`, even if there are 3 stopwords between `cotton` and `shirt`, they are ignored and we still give true. this is assumed from the following line in Assignment: `Store positions after the same tokenization/normalization/stemming pipeline used in Part A`)


### positional phrase search:
imported from `search/positional_index.py`
takes in the `query` and `positional_index`, is at endpoint `/phrase?query=`
only for match two words in consecutive order.
from `positional_index`, make a lookup dictionary for a term where `{doc_id: positions}` for each doc_id with that term
for the two words, get the lookup dictionaries, and start search in the `common_docs`

-> using a two-pointer approach, if term1 is exactly one position before term2, return the positions, else return `(-1, -1)`


### proximity term search:
imported from `search/positional_index.py`
takes in two terms, `term1` and `term2`, one WITHIN parameter `k`, `positional_index` is at endpoint `/proximity?term1=<ABC>&term2=<XYZ>&k=10`
match the two words within some distance between them, and they should be in order t1, t2.
use the same concept of positional phrase search, using two pointers, but this time use `if 0 < difference <= within_k` as the satisfying criteria, where `difference = positions_2[j] - positions_1[i]`.

-> using a two-pointer approach, if term1 is less than or equal to `k` word distance before term2, return the positions, else return `(-1, -1)`