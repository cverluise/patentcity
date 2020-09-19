import datetime
import json
import os
import re
from glob import glob
from zlib import adler32

import numpy as np
import pandas as pd
import typer

from patentcity_lib import GEOC_OUTCOLS

"""
General purpose utils
"""

# msg utils
ok = "\u2713"
not_ok = "\u2717"

app = typer.Typer()
TAG_RE = re.compile(r"<[^>]+>")
WHITE_RE = re.compile(r"\s+")


def clean_text(text, inDelim=None):
    """Remove anchors <*> and </*> and replace by an empty space"""
    text = TAG_RE.sub(" ", text)
    text = WHITE_RE.sub(" ", text)
    text = text.replace("\n", " ")
    if inDelim:
        text = text.replace(inDelim, " ")
    return text


def get_dt_human():
    """Return current datetime for human (e.g. 23/07/2020 11:30:59)"""
    return datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def get_recid(s):
    """Return the a uid made of the publication number and a random sequence 2^n random
    characters"""
    return adler32(s.encode())


def get_group(pubnum: int, u_bounds: str):
    u_bounds = [int(u_bound) for u_bound in u_bounds.split(",")]
    try:
        group = max(np.where(np.array(u_bounds) <= pubnum)[0]) + 2
    except ValueError:  # case where the pubnum is lower than any bound, hence in group 1
        group = 1
    return group


def get_pubnum(fname: str):
    try:
        pubnum = int(fname.split("-")[1])
    except ValueError:
        pubnum = None
        typer.secho(f"{not_ok}Pubnum is not int")
    return pubnum


def get_empty_here_schema():
    return {k: None for k in GEOC_OUTCOLS}


def flatten(l):
    return [item for sublist in l for item in sublist]


@app.command()
def make_groups(path: str, u_bounds: str = None):
    """Distribute files in folders by groups. u_bounds (upper bounds of the groups) should be
    ascending & comma-separated."""
    files = glob(path)
    [
        os.mkdir(os.path.join(os.path.dirname(path), f"group_{i + 1}"))
        for i in range(len(u_bounds.split(",")) + 1)
    ]
    for file in files:
        fname = os.path.basename(file)
        pubnum = get_pubnum(fname)
        if pubnum:
            group = get_group(pubnum, u_bounds)
            dest = os.path.join(os.path.dirname(file), f"group_{group}", fname)
            os.rename(file, dest)
            typer.secho(f"{ok}Move {file}->group_{group}/", fg=typer.colors.GREEN)


@app.command()
def prep_annotation_groups(path: str, u_bounds: str = None):
    """Print files as proper prodigy jsonl input. Include with a 'format' field indicating the
    format the document belongs to."""

    files = glob(path)
    for file in files:  # could be multi threaded but not worth it
        fname = os.path.basename(file)
        # path = os.path.join(dir, fname)
        pubnum = get_pubnum(fname)
        publication_number = fname.replace(".txt", "")
        group = get_group(pubnum, u_bounds)
        with open(file, "r") as fin:
            out = {
                "text": fin.read(),
                "publication_number": publication_number,
                "group": group,
            }
            typer.echo(json.dumps(out))


@app.command()
def get_whitespaced_labels(file: str):
    """Print info on labels with leading/trailing space.
    Expect a jsonl file with lines following a simple annotation model"""
    with open(file, "r") as lines:
        for i, line in enumerate(lines):
            line = json.loads(line)
            text = line["text"]
            spans = line.get("spans")
            if spans:
                for span in spans:
                    span_text = text[span["start"] : span["end"]]
                    startswith = span_text.startswith("\s")
                    endswith = span_text.endswith("\s")
                    if any([startswith, endswith]):
                        typer.secho(f"{json.dumps(line)}", fg=typer.colors.YELLOW)
                        typer.secho(
                            f"Span:{span}\nValue:{span_text}\nLine:{i + 1}",
                            fg=typer.colors.RED,
                        )


@app.command()
def model_report(model: str, pipes: str = "ner"):
    """Evaluate model"""

    scores = json.loads(open(os.path.join(model, "meta.json"), "r").read())["accuracy"]

    pipes = pipes.split(",")
    if "ner" in pipes:
        p, r, f = scores["ents_p"], scores["ents_r"], scores["ents_f"]
        typer.secho("NER Scores", fg=typer.colors.BLUE)
        typer.secho(f"{pd.DataFrame.from_dict(scores['ents_per_type'])}")
        typer.echo("-" * 37)
        typer.echo(f"ALL   %.2f  %.2f  %.2f" % (p, r, f))


@app.command()
def expand_pubdate_imputation(file: str, output: str = None):
    """Expand a sparse publication_date imputation file (with upper bound pubnum only) to a
    continuous (wrt pubnum) file."""
    df = pd.read_csv(file)
    max_pubnum = df.max()["pubnum"]
    expansion = pd.DataFrame(range(1, max_pubnum + 1), columns=["pubnum"])
    df_expansion = df.merge(expansion, how="right", left_on="pubnum", right_on="pubnum")
    df_expansion = df_expansion.fillna(method="backfill")
    for v in df_expansion.columns:
        df_expansion[v] = df_expansion[v].astype(int)
    df_expansion.to_csv(output)
    typer.secho(
        f"{ok} Imputation file expanded and saved in {output}", fg=typer.colors.GREEN
    )


@app.command()
def get_nomatch(file, index, inDelim: str = "|"):
    """Retrieve the search text from recId which were not matched

    FILE is the HERE batch geocoding API output
    INDEX is the corresponding HERE batch geocoding API input
    """

    def get_search_text_index(index, inDelim):
        search_text_index = {}
        with open(index, "r") as lines:
            for line in lines:
                recid, searchtext = line.split(inDelim)
                search_text_index.update({recid: searchtext})
        return search_text_index

    search_text_index = get_search_text_index(index, inDelim)

    with open(file, "r") as lines:
        for line in lines:
            if "NOMATCH" in line:
                recid = line.split(",")[0]
                search_text = search_text_index.get(recid)
                typer.secho(f"{recid}{inDelim}{search_text}")
            else:
                pass


if __name__ == "__main__":
    app()
