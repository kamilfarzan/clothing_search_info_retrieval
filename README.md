# clothing_search
## assignment for information retrieval

run fastAPI setup:

```bash
uv run uvicorn app:app --reload
```

### corpus:
imported using `search/loader.py`. 
there are 100 documents in the corpus, each with fields: DOCID, CATEGORY, TITLE & TEXT.

`document_blocks` are made using regex, and its constituent fields are also search using regex.

each field from the corpus is stored as a key, value pair in a document object, a raw entry of each complete unedited document is also stored. this object is then appended to the `docs` list and returned as the loaded corpus.


### preprocessing:
imported using `search/preprocess.py`.
preprocess of any text input does the following in order:
-> lowercases the `text`
-> removes any punctuation and extra white space, leaves alphanumerics and underscore
-> tokenizes the words (`word_tokenize` from `nltk`)
-> removes the stopwords from the `tokens` (standard nltk english stopwords, removes common words like the, is, and, of; this standard stopword set is used throughout the entire codebase)
-> stems the `filtered_tokens` (`PorterStemmer` from `nltk.stem`)

after this, return the `stemmed_tokens`.