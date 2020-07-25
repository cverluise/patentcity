import json
import os
from glob import iglob

import spacy
import typer

from patentcity_utils import clean_text, get_recid

app = typer.Typer()


def get_text(file, max_char):
    with open(file, "r") as fin:
        text = fin.read()[:max_char]
        publication_number = os.path.splitext(os.path.basename(file))[0]
        return " ".join([publication_number, text])


@app.command()
def beta(
        path: str, model: str = None, max_char: int = 1000, reduced_perf: bool = False,
        inDelim: str = None
):
    def serialize_beta(doc):
        labels = ["CIT", "ORG", "PERS", "LOC", "OCC"]
        publication_number, doc_ = doc[0].text, doc[1:]
        out = {"publication_number": publication_number}
        ents = doc_.ents
        for label in labels:
            out.update(
                {label.lower(): [clean_text(ent.text, inDelim) for ent in ents if ent.label_ ==
                                 label]})
        if out.get("loc"):
            # from loc: ["", ""] to loc: [{"raw":"", "id":""}, {...}]
            # -> should make it relatively efficient to integrate results back from here
            out.update({"loc": [{"raw": v, "recId": get_recid(publication_number)} for _, v in out[
                "loc"].items()]})
        typer.echo(json.dumps(out))

    nlp = spacy.load(model)
    blobs = iglob(path)
    texts = (get_text(file, max_char) for file in blobs)
    if reduced_perf:
        docs = nlp.pipe(texts, n_threads=1, batch_size=1)
    else:
        docs = nlp.pipe(texts)
    for doc in docs:
        serialize_beta(doc)


if __name__ == "__main__":
    app()
