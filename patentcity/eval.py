import json
import os

import numpy as np
import pandas as pd
import typer

from patentcity.utils import get_cit_code

app = typer.Typer()


@app.command()
def spacy_model(model: str, pipes: str = "ner"):
    """Evaluate model*

    *Actually report results from runtime eval
    """

    scores = json.loads(open(os.path.join(model, "meta.json"), "r").read())["accuracy"]

    pipes = pipes.split(",")
    if "ner" in pipes:
        p, r, f = scores["ents_p"], scores["ents_r"], scores["ents_f"]
        typer.secho("NER Scores", fg=typer.colors.BLUE)
        typer.echo(f"{pd.DataFrame.from_dict(scores['ents_per_type']).round(2)}")
        typer.echo("-" * 37)
        typer.echo(f"ALL   %.2f  %.2f  %.2f" % (p, r, f))


@app.command()
def cit_fst(
    test_file, fst_file: str = None, fuzzy_match: bool = True, verbose: bool = False
):
    """Evaluate cit FST on TEST_FILE"""
    fst = json.loads(open(fst_file, "r").read())
    test_df = pd.read_csv(test_file, sep=";")
    test_df = test_df.replace({np.nan: None})

    res = []
    for i, row in test_df.iterrows():
        text = row["text"]
        pred = get_cit_code(text, fst, fuzzy_match)
        res += [
            [row["publication_number"], text, row["gold"], pred, row["gold"] == pred]
        ]
    res = pd.DataFrame(
        res, columns=["publication_number", "text", "gold", "pred", "res"]
    )
    errors = res.query("res==False")

    filename = os.path.basename(test_file)

    acc = 1 - len(errors) / len(res)
    typer.secho(f"## {filename}\n", fg=typer.colors.BLUE)
    typer.echo(f"Accuracy (fuzzy-match {fuzzy_match}): {acc * 100:.2f}%\n")
    if verbose:
        typer.echo(f"### Errors\n{errors.to_markdown()}")


if __name__ == "__main__":
    app()
