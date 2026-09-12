from fastapi import FastAPI
from fastapi.responses import FileResponse
from search.loader import load_corpus
from search.preprocess import preprocess
from search.inverted_index import make_inverted_index
from search.vsm import build_document_vectors, search
from search.positional_index import make_positional_index, phrase_search, proximity_search


corpus = load_corpus("data/corpus_100.txt")
# print(f"{type(corpus)}, Documents: {len(corpus)}, Each Document Type: {type(corpus[0])} \nFirst doc: {corpus[0]}")

for document in corpus:
    document["tokens"] = preprocess(document["text"])

inverted_index = make_inverted_index(corpus)
positional_index = make_positional_index(corpus)
document_vectors, document_norms = build_document_vectors(inverted_index)
# print(preprocess(corpus[0]["text"]))
# print(corpus[0]["text"])

app = FastAPI()
@app.get("/")
def home():
    return FileResponse("static/index.html")

@app.get("/search")
def run_search(query: str, k: int = 10):
    return search(query, inverted_index, document_vectors, document_norms, preprocess, len(corpus), k)

@app.get("/phrase")
def phrase(query: str):
    return phrase_search(query, positional_index, preprocess)

@app.get("/proximity")
def proximity(term1: str, term2: str, k: int):
    return proximity_search(term1, term2, k, positional_index, preprocess)