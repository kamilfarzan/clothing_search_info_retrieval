from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from search.loader import load_corpus
from search.preprocess import preprocess
from search.inverted_index import make_inverted_index
from search.vsm import build_document_vectors, search
from search.positional_index import make_positional_index, phrase_search, proximity_search


corpus = load_corpus("data/corpus_100.txt")

for document in corpus:
    document["tokens"] = preprocess(document["text"])

inverted_index = make_inverted_index(corpus)
positional_index = make_positional_index(corpus)
document_vectors, document_norms = build_document_vectors(inverted_index)

corpus_by_id = {doc["doc_id"]: doc for doc in corpus}

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def home():
    return FileResponse("static/index.html")


@app.get("/documents")
def documents_page():
    return FileResponse("static/documents.html")


@app.get("/docs_info")
def get_documents_info():
    return [
        {
            "doc_id": doc.get("doc_id", ""),
            "title": doc.get("title", ""),
            "category": doc.get("category", ""),
            "tokens": doc.get("tokens", []),
        }
        for doc in corpus
    ]


@app.get("/search")
def run_search(q: str | None = None, query: str | None = None, k: int = 10):
    search_query = q if q is not None else (query or "")
    if not search_query.strip():
        return []

    raw_results = search(
        search_query,
        inverted_index,
        document_vectors,
        document_norms,
        preprocess,
        len(corpus),
        k,
    )

    # when returning, keep it good enough to show off in the frontend
    enriched = [] 
    for doc_id, score in raw_results:
        doc = corpus_by_id.get(doc_id, {})
        enriched.append(
            {
                "doc_id": doc_id,
                "title": doc.get("title", ""),
                "category": doc.get("category", ""),
                "score": round(float(score), 4),
            }
        )
    return enriched


@app.get("/phrase")
def phrase(q: str | None = None, query: str | None = None):
    phrase_query = q if q is not None else (query or "")
    if not phrase_query.strip():
        return []

    terms = preprocess(phrase_query)
    if len(terms) != 2:
        raise HTTPException(
            status_code=400,
            detail="Phrase search requires exactly two valid terms.",
        )

    try:
        raw_results = phrase_search(phrase_query, positional_index, preprocess)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))



    # when returning, keep it good enough to show off in the frontend
    enriched = []
    for item in raw_results:
        doc_id = item["doc_id"]
        doc = corpus_by_id.get(doc_id, {})
        positions = item.get("positions", {})
        enriched.append(
            {
                "doc_id": doc_id,
                "title": doc.get("title", ""),
                "category": doc.get("category", ""),
                "positions": positions,
                "distance": 1,
            }
        )
    return enriched[:10]


@app.get("/proximity")
def proximity(
    q: str | None = None,
    query: str | None = None,
    term1: str | None = None,
    term2: str | None = None,
    k: int | None = None,
):
    if k is None or k <= 0:
        raise HTTPException(
            status_code=400, detail="Parameter 'k' must be a positive integer."
        )

    t1, t2 = term1, term2
    if not t1 or not t2:
        prox_query = q if q is not None else (query or "")
        tokens = preprocess(prox_query)
        if len(tokens) != 2:
            raise HTTPException(
                status_code=400,
                detail="Proximity search requires exactly two valid terms.",
            )
        t1, t2 = tokens[0], tokens[1]

    try:
        raw_results = proximity_search(
            t1, t2, k, positional_index, preprocess
        )
    except (ValueError, IndexError):
        raise HTTPException(
            status_code=400,
            detail="Proximity search requires two valid terms.",
        )


    # when returning, keep it good enough to show off in the frontend
    enriched = []
    for item in raw_results:
        doc_id = item["doc_id"]
        doc = corpus_by_id.get(doc_id, {})
        positions = item.get("positions", {})
        pos_values = list(positions.values())
        dist = abs(pos_values[1] - pos_values[0]) if len(pos_values) >= 2 else 0
        enriched.append(
            {
                "doc_id": doc_id,
                "title": doc.get("title", ""),
                "category": doc.get("category", ""),
                "positions": positions,
                "distance": dist,
            }
        )
    return enriched[:10]