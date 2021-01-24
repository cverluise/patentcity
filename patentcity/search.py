import yaml
import typer
import os

app = typer.Typer()


@app.command()
def relationship_params(config_search):
    """Generate config files for grid defined by CONFIG_SEARCH"""
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
                with open(os.path.join(path, filename.replace("search", str(i))), "w") as file:
                    yaml.dump(base, file)
        typer.secho(f"config files saved in {path}", fg=typer.colors.BLUE)


if __name__ == "__main__":
    app()

