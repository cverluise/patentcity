import json
import os

import numpy as np
import pandas as pd
import typer
import yaml

from patentcity.utils import get_cit_code
from patentcity.relationship import get_child, RELATIONS

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


@app.command()
def relationship_model(file, config, report: str = "short"):
    """
    Evaluate relationship model for a given set of parameters (in yaml config file)
    """
    assert report in ["short", "long", "json"]

    def eval_performance(pred, gold, label: str = None):
        def get_rel(relations, label):
            rel = [
                {
                    "head": [
                        rel["head_span"]["token_start"],
                        rel["head_span"]["token_end"],
                    ],
                    "child": [
                        rel["child_span"]["token_start"],
                        rel["child_span"]["token_end"],
                    ],
                    "label": rel["label"],
                }
                for rel in relations
            ]
            if label:
                rel = [rel_ for rel_ in rel if rel_["label"] == label]
            return rel

        rel_pred = get_rel(pred, label)
        rel_gold = get_rel(gold, label)

        true = list(rel_gold)
        true_positives = [rel for rel in rel_pred if rel in rel_gold]
        false_positives = [rel for rel in rel_pred if rel not in rel_gold]
        false_negatives = [rel for rel in rel_gold if rel not in rel_pred]
        return true, true_positives, false_positives, false_negatives

    def report_errors(errors):
        # an error is expressed as a rel with tokens
        # {"head": [head_start, head_end], "child": [child_start, child_end], "label": label,
        # "tokens": list}

        def report_error(error):
            tokens = error["tokens"]

            def get_text(tokens, boundaries):
                text = tokens[boundaries[0] : boundaries[1] + 1]
                text = " ".join(text).replace("\n", "")
                return text

            start = min(error["head"][0], error["child"][0])
            end = max(error["head"][1], error["child"][1])
            error_rel = f"""{get_text(tokens, error['head'])}({error['head']})->-{error['label']}->-{get_text(tokens, error['child'])}({error['child']})""".replace(
                "\n", ""
            )
            error_context = f"""{get_text(tokens, [start, end])}"""

            return f"{error_rel}\n{error_context}"

        for error in errors:
            typer.echo(report_error(error))

    def get_relation(head, child):
        relation = []
        if child:
            for child_ in child:
                # nb: in some configs (max_n >1), there might be more than 1 child
                # here generate something in the flavor of eg["relations"] for eval
                relation += [
                    {
                        "child": child_["token_end"],
                        "child_span": child_,
                        "head": head["token_end"],
                        "head_span": head,
                        "label": RELATIONS[child_["label"]],
                    }
                ]
        return relation

    def get_report(truth_categories, report):
        def filter_relation(label, *args):
            assert label in list(RELATIONS.values())
            for l in args:
                yield [e for e in l if e["label"] == label]

        def get_metrics(
            true, true_positives, false_positives, false_negatives, label=None
        ):
            if label:
                true, true_positives, false_positives, false_negatives = filter_relation(
                    label, true, true_positives, false_positives, false_negatives
                )
            # nb_t = len(true)
            nb_tp = len(true_positives)
            nb_fp = len(false_positives)
            nb_fn = len(false_negatives)

            prec = nb_tp / (nb_tp + nb_fp)
            rec = nb_tp / (nb_tp + nb_fn)
            f1 = 2 * prec * rec / (prec + rec)

            return prec, rec, f1

        true, true_positives, false_positives, false_negatives = truth_categories

        res = {}
        for label in [None] + list(RELATIONS.values()):
            prec, rec, f1 = get_metrics(
                true, true_positives, false_positives, false_negatives, label
            )
            label = label if label else "ALL"
            res.update(
                {label: {"p": round(prec, 3), "r": round(rec, 3), "f": round(f1, 3)}}
            )
        if report == "json":
            typer.echo(json.dumps(res))
        else:
            typer.secho("\n# Report", fg=typer.colors.BLUE)
            typer.echo(f"Config file: {config}")
            typer.secho("\n## Performance", fg=typer.colors.BLUE)
            typer.echo(pd.DataFrame.from_dict(res).to_markdown())
            if report == "long":
                typer.secho("\n## False positives", fg=typer.colors.BLUE)
                report_errors(sorted(false_positives, key=lambda d: d["label"]))
                typer.secho("\n## False negatives", fg=typer.colors.BLUE)
                report_errors(sorted(false_negatives, key=lambda d: d["label"]))

    true, true_positives, false_positives, false_negatives = [], [], [], []
    with open(config, "r") as config_file:
        cfg = yaml.load(config_file, Loader=yaml.FullLoader)
    with open(file, "r") as lines:
        for line in lines:
            eg = json.loads(line)
            ents = eg["spans"]
            relations_gold = eg["relations"]

            heads = [ent for ent in ents if ent["label"] in ["ASG", "INV"]]
            children = [ent for ent in ents if ent["label"] not in ["ASG", "INV"]]

            relations_pred = []
            for head in heads:
                for label in ["LOC", "OCC", "CIT"]:
                    cfg_ = cfg[label]
                    child = get_child(
                        head,
                        children,
                        label,
                        cfg_["max_length"],
                        cfg_["position"],
                        cfg_["max_n"],
                    )

                    relations_pred += get_relation(head, child)

            true_, true_positives_, false_positives_, false_negatives_ = eval_performance(
                relations_pred, relations_gold
            )

            true += true_
            true_positives += true_positives_
            false_positives += [
                {**fp, **{"tokens": [tok["text"] for tok in eg["tokens"]]}}
                for fp in false_positives_
            ]
            false_negatives += [
                {**fn, **{"tokens": [tok["text"] for tok in eg["tokens"]]}}
                for fn in false_negatives_
            ]
    get_report((true, true_positives, false_positives, false_negatives), report)


if __name__ == "__main__":
    app()
