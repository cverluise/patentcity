import json
import os
from concurrent.futures import ThreadPoolExecutor
from glob import glob, iglob
from hashlib import md5
from itertools import combinations, repeat
from pathlib import Path

import git
import spacy
import typer
import yaml
from Levenshtein import distance as levenshtein_distance
from smart_open import open

from patentcity.relationship import create_relationship_component
from patentcity.utils import clean_text, get_cit_code, get_recid

"""
                             Brew patentcity dataset

General functioning: Stream text blobs | process | print json blobs to stdout

* beta: entities only
* v1: entities & relationship
"""

app = typer.Typer()
repo = git.Repo(search_parent_directories=True)
sha = repo.head.object.hexsha


def _get_blob(file: str):
    with open(file, "r") as fin:
        text = fin.read()
        publication_number = os.path.splitext(os.path.basename(file))[0]
        hash_id = md5(text.encode()).hexdigest()
    typer.echo(
        json.dumps(
            {"publication_number": publication_number, "text": text, "hash_id": hash_id}
        )
    )


@app.command(name="v1.grind")
def grind(path: str, max_workers: int = 10):
    """Stream texts in `path` and return json objects to stdout. Files are expected to be patent texts named after the
    publication_number of the patent (e.g. US-12345-A.txt).


    Arguments:
        path: data path, wildcard allowed
        max_workers: max number of workers

    **Output**:
        ```json
        {"publication_number": str, "text": str, "hash_id": str}
        ```

    **Usage:**
        ```shell
        patencity brew v1.grind "data/US/*.txt"
        # Nb: if the file is large, you can split and zip
        ```
    """
    files = iglob(path)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(_get_blob, files)


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
    Stream json objects in `path` and return json v1 objects to stdout.

    Arguments:
        path: data path, wildcard allowed
        model: model path
        rel_config: relationship resolution config file path
        max_char: max char considered for entity extraction
        batch_size: size of the data batch passed to spaCy model
        inDelim: in delimiter

    **Output**:
        ```json
        {"publication_number": str, "patentee": List[dict], "hash_id": str,
        "model_ents": str, "model_rels": str, "git_sha": str}
        ```

    **Usage:**
        ```shell
        patencity brew v1 "data/US/uspatentxx*.jsonl"
        # Nb: if the file is large, you can split and zip
        ```
    """
    nlp = spacy.load(model)
    with open(rel_config, "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)
    nlp.add_pipe("relation_extractor", config={"config": config}, last=True)

    files = glob(path)
    for file in files:
        publication_numbers = list(
            (json.loads(line)["publication_number"] for line in open(file, "r"))
        )
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


def _topping(line, config):
    line = json.loads(line)
    country_code, pubnum, _ = line["publication_number"].split("-")
    pubnum = int(pubnum)
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
        if cit_text:
            cit_code = get_cit_code(cit_text, config["cit_code"]["XX"], True)
            patentee.update({"cit_code": cit_code})
        patentees_ += [patentee]
    nb_patee = len(patentees_) if patentees_ else 0
    nb_inv = sum([patentee_.get("is_inv") for patentee_ in patentees_])
    nb_asg = sum([patentee_.get("is_asg") for patentee_ in patentees_])
    line.update({"patentee": patentees_})

    if country_code in config["deduplicate"].keys():
        pubnum_low, pubnum_up = config["deduplicate"][country_code]["pubnum"].split("-")
        pubnum_low, pubnum_up = int(pubnum_low), int(pubnum_up)
        if pubnum_low <= pubnum <= pubnum_up:
            line = _deduplicate(line, config["deduplicate"][country_code]["threshold"])
            nb_patee_dupl = len(
                [
                    patentee
                    for patentee in line.get("patentee")
                    if patentee["is_duplicate"]
                ]
            )
            nb_inv_dupl = len(
                [
                    patentee
                    for patentee in line.get("patentee")
                    if patentee["is_inv"] and patentee["is_duplicate"]
                ]
            )
            nb_asg_dupl = len(
                [
                    patentee
                    for patentee in line.get("patentee")
                    if patentee["is_asg"] and patentee["is_duplicate"]
                ]
            )
            nb_patee = nb_patee - nb_patee_dupl
            nb_inv = nb_inv - nb_inv_dupl
            nb_asg = nb_asg - nb_asg_dupl

    line.update({"nb_patee": nb_patee, "nb_inv": nb_inv, "nb_asg": nb_asg})

    typer.echo(json.dumps(line))


def _deduplicate(line: dict, threshold: float):
    """Return LINE with an additional field is_duplicate (bool). is_duplicate is True when the patentee should be
    removed from the analysis because another patentee has the 'same' name. We say that 2 patentees have the same name
     when the relative levenshtein of the two strings (lower) is below THRESHOLD."""
    # line = json.loads(line)
    patentees = line.get("patentee")
    [patentee.update({"is_duplicate": False}) for patentee in patentees]
    if patentees:
        for i, j in list(combinations(range(len(patentees)), 2)):
            p1, p2 = patentees[i], patentees[j]
            name1 = p1.get("name_text").lower()
            name2 = p2.get("name_text").lower()
            lev_dist_rel = levenshtein_distance(name1, name2) / (
                (len(name1) + len(name2)) / 2
            )
            are_duplicates = True if lev_dist_rel < threshold else False
            # print(name1, name2, are_duplicates, lev_dist_rel)
            if are_duplicates:
                p1_hasloc, p2_has_loc = p1.get("loc_text"), p2.get("loc_text")
                if p1_hasloc == p2_has_loc:  # case when both have loc or none has loc
                    if len(p1.keys()) >= len(p2.keys()):  # we 'keep' p1
                        p1.update(
                            {"is_duplicate": any([False, p1.get("is_duplicate")])}
                        )
                        p2.update({"is_duplicate": any([True, p2.get("is_duplicate")])})
                    else:  # we 'keep' p2
                        p1.update({"is_duplicate": any([True, p1.get("is_duplicate")])})
                        p2.update(
                            {"is_duplicate": any([False, p2.get("is_duplicate")])}
                        )
                else:  # only one of the 2 has loc
                    if p1_hasloc:  # we 'keep' p1
                        p1.update(
                            {"is_duplicate": any([False, p1.get("is_duplicate")])}
                        )
                        p2.update({"is_duplicate": any([True, p2.get("is_duplicate")])})
                    else:  # we 'keep' p2
                        p1.update({"is_duplicate": any([True, p1.get("is_duplicate")])})
                        p2.update(
                            {"is_duplicate": any([False, p2.get("is_duplicate")])}
                        )
                patentees[i] = p1
                patentees[j] = p2
        line.update({"patentee": patentees})
    return line


@app.command(name="v1.topping")
def topping(file: str, config_file: str = None, max_workers=10):
    """Stream data in `file` and  return enriched v1 json object to stdout.

    Arguments:
        file: file path
        config_file: topping config file
        max_workers: max number of workers

    **Output**:
        ```json
        {"publication_number": str, "patentee": List[dict], "hash_id": str,
        "model_ents": str, "model_rels": str, "git_sha": str}
        ```

    **Usage:**
        ```shell
        mv data/US/entrel_uspatentxx.jsonl data/US/entrel_uspatentxx.jsonl.tmp
        patencity v1.topping --config-file configs/top_xxpatentxx.yaml "data/US/entrel_uspatentxx.jsonl.tmp"
        # Nb: if the file is large, you can split and zip
        ```

    """
    with open(config_file, "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)
    for k, v in config["cit_code"].items():
        config["cit_code"].update({k: json.loads(open(v, "r").read())})

    with open(file, "r") as lines:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            executor.map(_topping, lines, repeat(config))


if __name__ == "__main__":
    app()
