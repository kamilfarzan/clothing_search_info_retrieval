from fastapi import FastAPI
from fastapi.responses import FileResponse
from search.loader import load_corpus


corpus = load_corpus("data/corpus_100.txt")
print(f"{type(corpus)}, Documents: {len(corpus)}, Each Document Type: {type(corpus[0])} \nFirst doc: {corpus[0]}")


app = FastAPI()
@app.get("/")
def home():
    return FileResponse("static/index.html")