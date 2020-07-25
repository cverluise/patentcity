import csv
import datetime
import json
import os
import re
import secrets

import pandas as pd
import typer

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


def get_recid(publication_number, n: int = 2):
    """Return the a uid made of the publication number and a random sequence 2^n random
    characters"""
    id = secrets.token_hex(n)
    return "_".join([publication_number, id])


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
        typer.echo(f"ALL   %.6f  %.6f  %.6f" % (p, r, f))


if __name__ == "__main__":
    app()
