import os
from glob import glob

import pandas as pd
import typer
import yaml

from patentcity.relationship import RELATIONS

app = typer.Typer()


@app.command()
def relationship_params(config_search: str):
    """Generate config files defined by `config_search` grid

    Arguments:
        config_search: config search file path

    **Usage:**
        ```shell
        patentcity search relationship-params configs/rel_search.yaml
        ``
    """
    filename = os.path.basename(config_search)
    path = os.path.dirname(config_search)
    with open(config_search, "r") as config_file:
        cfg = yaml.load(config_file, Loader=yaml.FullLoader)
        search = cfg["search"]
        base = cfg["base"]

        for param in search.keys():
            try:
                start, end = list(map(lambda x: int(x), search[param].split("-")))
                grid = range(start, end)
            except ValueError:
                grid = search[param].split("-")

            for i, val in enumerate(grid):
                for label in base.keys():
                    base[label].update({param: val})
                with open(
                    os.path.join(path, filename.replace("search", str(i))), "w"
                ) as file:
                    yaml.dump(base, file)
        typer.secho(f"config files saved in {path}", fg=typer.colors.BLUE)


@app.command()
def relationship_best(path: str, report: str = "short"):
    """Report perf of each (long)/best (short) config`

    Arguments:
        path: data file path (wildcard allowed)
        report: report type (in ["short", "long"])

    **Usage:**
        ```shell
        patentcity eval relationship-model data/gold_rel_ddpatent01.jsonl rel_ddpatent01.yaml --report json
        ```
    """
    files = glob(path)
    assert report in ["short", "long"]

    res = pd.DataFrame()
    for file in files:
        tmp = pd.read_json(file).T
        tmp["config"] = os.path.basename(file)
        res = res.append(tmp)
    res = res.reset_index().rename(columns={"index": "label"})

    labels = ["ALL"] + list(RELATIONS.values())
    for i, label in enumerate(labels):
        res_label = res.query(f"label=='{label}'").sort_values("f", ascending=False)
        if report == "long":
            if i == 0:
                typer.secho(f"# Report", fg=typer.colors.BLUE)
            typer.secho(f"\n## {label}", fg=typer.colors.BLUE)
            typer.echo(res_label.to_markdown(index=False))
        else:
            if i == 0:
                best = pd.DataFrame(columns=res_label.columns)
            best = best.append(res_label.iloc[:1])
    if report == "short":
        typer.echo(best.to_markdown(index=False))


if __name__ == "__main__":
    app()
