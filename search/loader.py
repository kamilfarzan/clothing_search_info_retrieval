import re
from pathlib import Path

def load_corpus(path) -> list[dict[str, str]]:
    corpus_text = Path(path).read_text(encoding="utf-8")
    docs = []
    fields = {
        "doc_id": "DOCID",
        "category": "CATEGORY",
        "title": "TITLE",
        "text": "TEXT"
    }

    # find DOC tags
    document_blocks = re.findall(r"<DOC>(.*?)<\/DOC>", corpus_text, re.DOTALL) # use re.DOTALL to get all characters (even newline)
    # print(document_blocks, type(document_blocks), len(document_blocks), "\n")

    for document in document_blocks:
        document_object = {}

        for key, field in fields.items():
            reg_exp_for_field = fr"<{field}>(.*?)<\/{field}>"
            field_match = re.search(reg_exp_for_field, document, re.DOTALL)

            if field_match:
                document_object[key] = field_match.group(1).strip()

        # document_object["doc_id"] = re.search(r"<DOCID>(.*?)<\/DOCID>", document, re.DOTALL)
        # document_object["category"] = re.search(r"<CATEGORY>(.*?)<\/CATEGORY>", document, re.DOTALL)
        # document_object["title"] = re.search(r"<TITLE>(.*?)<\/TITLE>", document, re.DOTALL)
        # document_object["text"] = re.search(r"<TEXT>(.*?)<\/TEXT>", document, re.DOTALL)


        # # keep raw XML format (might need it as whole?)
        document_object["raw"] = document

        docs.append(document_object)

    return docs