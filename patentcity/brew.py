import json
import yaml
import os
from glob import iglob, glob
from smart_open import open
import git
from concurrent.futures import ThreadPoolExecutor
from itertools import repeat

from patentcity.relationship import create_relationship_component
import spacy
import typer
from hashlib import md5

from patentcity.utils import clean_text, get_recid, get_cit_code

"""
                             Brew patentcity dataset

General functioning: Stream text blobs | process through spaCy model | print json blobs to stdout
* Beta: entities only, no dependency parsing
"""

app = typer.Typer()
repo = git.Repo(search_parent_directories=True)
sha = repo.head.object.hexsha


def get_text(file, max_char=None):
    with open(file, "r") as fin:
        text = fin.read()[:max_char] if max_char else fin.read()
        return text


@app.command(deprecated=True)
def beta(
    path: str,
    model: str = None,
    max_char: int = None,
    reduced_perf: bool = False,
    inDelim: str = "|",
):
    """Print json blobs of the beta dataset

    {"publication_number": str,
    "pers": List[str],
    "org":List[str],
    "loc":List[Dict("raw":"", "recId":"")],
    "occ":List[str],
    "cit":List[str]}"""

    def serialize_blob(doc):
        publication_number, doc_ = doc[0].text, doc[1:]
        out = {"publication_number": publication_number}
        ents = doc_.ents
        labels = set([ent.label_ for ent in ents])
        for label in labels:
            out.update(
                {
                    label.lower(): [
                        {
                            "text": clean_text(ent.text, inDelim),
                            "start": ent.start,
                            "end": ent.end,
                        }
                        for ent in ents
                        if ent.label_ == label
                    ]
                }
            )
        if out.get("loc"):
            # from loc: ["", ""] to loc: [{"raw":"", "recId":""}, {...}]
            # -> should make it relatively efficient to integrate results back from here
            out.update(
                {
                    "loc": [
                        {
                            "raw": loc_["text"],
                            "recId": get_recid(loc_["text"]),
                            "start": loc_["start"],
                            "end": loc_["end"],
                        }
                        for loc_ in out["loc"]
                    ]
                }
            )
        typer.echo(json.dumps(out))

    nlp = spacy.load(model)
    blobs = iglob(path)
    texts = (get_text(file, max_char) for file in blobs)
    if reduced_perf:
        docs = nlp.pipe(texts, n_threads=1, batch_size=1)
    else:
        docs = nlp.pipe(texts)
    for doc in docs:
        serialize_blob(doc)


@app.command()
def v1(
    path: str,
    model: str,
    rel_config: str,
    max_char: int = 9999,
    batch_size: int = 1000,
    inDelim: str = "|",
):
    """
    Print jsonl blobs of the v1 dataset
    """
    nlp = spacy.load(model)
    with open(rel_config, "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)
    nlp.add_pipe("relation_extractor", config={"config": config}, last=True)

    files = glob(path)
    for file in files:
        publication_numbers = list((json.loads(line)["publication_number"] for line in open(file, "r")))
        hash_ids = list((json.loads(line)["hash_id"] for line in open(file, "r")))
        with open(file, "r") as lines:
            texts = (json.loads(line)["text"][:max_char] for line in lines)
            docs = nlp.pipe(texts, batch_size=batch_size)
            for i, doc in enumerate(docs):
                publication_number = publication_numbers[i]
                hash_id = hash_ids[i]
                patentees = [
                    {k: clean_text(v, inDelim) for k, v in patentee.items()}
                    for patentee in doc._.patentees
                ]
                row = {
                    "publication_number": publication_number,
                    "patentee": patentees,
                    "hash_id": hash_id,
                    "model_ents": model,
                    "model_rels": rel_config,
                    "git_sha": sha,
                }
                typer.echo(json.dumps(row))


def topping_(line, cit_fst):
    line = json.loads(line)
    patentees_ = []
    patentees = line["patentee"]
    for patentee in patentees:
        name_label = patentee.get("name_label")
        loc_text = patentee.get("loc_text")
        cit_text = patentee.get("cit_text")
        is_inv = name_label == "INV"
        is_asg = name_label == "ASG"
        patentee.update({"is_asg": is_asg, "is_inv": is_inv})
        if loc_text:
            patentee.update({"loc_recId": get_recid(loc_text)})
        if cit_text and cit_fst:
            cit_code = get_cit_code(cit_text, cit_fst, True)
            patentee.update({"cit_code": cit_code})
        patentees_ += [patentee]
    line.update({"patentee": patentees_})
    typer.echo(json.dumps(line))


@app.command(name="v1.topping")
def topping(file: str, cit_fst_file: str = None, max_workers=10):
    """Return patentees with v1 var derived from extracted vars (is_asg, is_inv, etc)"""

    cit_fst = json.loads(open(cit_fst_file, "r").read()) if cit_fst_file else None
    with open(file, "r") as lines:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            executor.map(topping_, lines, repeat(cit_fst))


if __name__ == "__main__":
    app()
