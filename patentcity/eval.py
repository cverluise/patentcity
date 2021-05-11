import json
import os
from typing import List
import numpy as np
import pandas as pd
import typer
import yaml

from patentcity.utils import get_cit_code
from patentcity.relationship import get_child, RELATIONS

"""
                            Eval patentcity model components

Take model (and test data, opt) and return performance metrics report
"""

app = typer.Typer()


@app.command()
def spacy_model(model: str, components: str = "ner"):
    """Evaluate spaCy model `components` and return report to stdout. Notes: i) only "ner" component is supported so far ii) report results from runtime eval

    Arguments:
        model: model path
        components: spaCy model components (comma separated)

    **Usage:**
        ```shell
        patentcity eval spacy-model models/en_ent_uspatent01
        ```

    """

    scores = json.loads(open(os.path.join(model, "meta.json"), "r").read())[
        "performance"
    ]

    components = components.split(",")
    if "ner" in components:
        p, r, f = scores["ents_p"], scores["ents_r"], scores["ents_f"]
        typer.secho("NER Scores", fg=typer.colors.BLUE)
        perfs = pd.DataFrame.from_dict(scores["ents_per_type"])
        perfs["ALL"] = (p, r, f)
        perfs = perfs.round(2)
        perfs = perfs[sorted(perfs.columns)]
        typer.echo(f"{perfs.to_markdown()}")


@app.command()
def cit_fst(
    test_file: str,
    fst_file: str = None,
    fuzzy_match: bool = True,
    verbose: bool = False,
):
    """Evaluate citizenship finite state transducer and return report to stdout

    Arguments:
        test_file: test file path
        fst_file: fst file path
        fuzzy_match: accept/reject fuzzy match
        verbose: report verbosity

    **Usage:**
    """
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
def relationship_model(test_file: str, rel_config: str, report: str = "short"):
    """
    Evaluate relationship model and return report to stdout

    Arguments:
        test_file: test file path
        rel_config: relationship resolution config file path
        report: size and format of the performance report (in "short", "long", "json")

    **Usage:**
        ```shell
        patentcity eval relationship-model gold_rel_uspatent01.jsonl configs/rel_uspatent01.yaml
        ```
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

            return error_rel, error_context

        data = []
        for error in errors:
            data += [report_error(error)]
        typer.echo(
            pd.DataFrame(columns=["error_rel", "error_context"], data=data).to_markdown(
                index=False
            )
        )

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
            try:
                prec = nb_tp / (nb_tp + nb_fp)
                rec = nb_tp / (nb_tp + nb_fn)
                f1 = 2 * prec * rec / (prec + rec)
            except ZeroDivisionError:
                rec = prec = f1 = None

            return prec, rec, f1

        true, true_positives, false_positives, false_negatives = truth_categories

        res = {}
        for label in [None] + list(RELATIONS.values()):
            prec, rec, f1 = get_metrics(
                true, true_positives, false_positives, false_negatives, label
            )
            label = label if label else "ALL"
            if all([prec, rec, f1]):
                res.update(
                    {
                        label: {
                            "p": round(prec, 3),
                            "r": round(rec, 3),
                            "f": round(f1, 3),
                        }
                    }
                )
            else:
                res.update({label: {"p": None, "r": None, "f": None}})

        if report == "json":
            typer.echo(json.dumps(res))
        else:
            typer.secho("\n# Report", fg=typer.colors.BLUE)
            typer.echo(f"Config file: {rel_config}")
            typer.secho("\n## Performance", fg=typer.colors.BLUE)
            typer.echo(pd.DataFrame.from_dict(res).to_markdown())
            if report == "long":
                typer.secho("\n## False positives", fg=typer.colors.BLUE)
                report_errors(sorted(false_positives, key=lambda d: d["label"]))
                typer.secho("\n## False negatives", fg=typer.colors.BLUE)
                report_errors(sorted(false_negatives, key=lambda d: d["label"]))

    true, true_positives, false_positives, false_negatives = [], [], [], []
    with open(rel_config, "r") as config_file:
        cfg = yaml.load(config_file, Loader=yaml.FullLoader)
    with open(test_file, "r") as lines:
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


@app.command()
def patentee_deduplication(test_file: str, verbose: bool = False):
    """Evaluate patentee deduplication and return the best threshold and related deduplication accuracy to stdout.
    Note: Deduplication is based on the relative levenshtein edit distance.

    Arguments:
        test_file: test file path
        verbose: report verbosity

    **Usage:**
        ```shell
        patentcity eval patentee-deduplication data/gold_deduplication_uspatent01.jsonl
        ```
    """
    df = pd.read_json(test_file, lines=True)
    df["clas"] = df["answer"].apply(
        lambda x: 0 if x == "reject" else (1 if x == "accept" else None)
    )
    df = df.query("clas==clas").copy()
    accuracy = {}
    for threshold in np.arange(0, 2, 0.01):
        df["pred"] = df["lev_dist_rel"].apply(lambda x: 1 if x < threshold else 0)
        nb_true = len(df.query("clas==pred"))
        acc = nb_true / len(df)
        accuracy.update({threshold: acc})
    accuracy = pd.DataFrame.from_dict(accuracy, orient="index", columns=["accuracy"])
    if verbose:
        typer.secho("## Levenshtein distance (rel) distribution", fg=typer.colors.BLUE)
        typer.echo(
            (
                df.groupby("answer")
                .describe(percentiles=np.arange(0, 1, 0.01))["lev_dist_rel"]
                .filter(regex="%")
                .T.to_markdown()
            )
        )
    threshold_star, accuracy_star = (
        accuracy.idxmax().values[0],
        accuracy.max().values[0],
    )
    typer.secho("## Best", fg=typer.colors.BLUE)
    typer.echo(f"Best threshold: {threshold_star}\nAccuracy: {accuracy_star}")


if __name__ == "__main__":
    app()
