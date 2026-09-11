from fastapi import FastAPI
from fastapi.responses import FileResponse
from search.loader import load_corpus
from search.preprocess import preprocess


corpus = load_corpus("data/corpus_100.txt")
# print(f"{type(corpus)}, Documents: {len(corpus)}, Each Document Type: {type(corpus[0])} \nFirst doc: {corpus[0]}")

print(preprocess(corpus[0]["text"]))
print(corpus[0]["text"])

app = FastAPI()
@app.get("/")
def home():
    return FileResponse("static/index.html")