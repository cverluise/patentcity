import typer
from patentcity import geo
from patentcity import brew
from patentcity import utils
from patentcity import io
from patentcity import eval
from patentcity import search

app = typer.Typer()

app.add_typer(geo.app, name="geo")
app.add_typer(brew.app, name="brew")
app.add_typer(io.app, name="io")
app.add_typer(utils.app, name="utils")
app.add_typer(eval.app, name="eval")
app.add_typer(search.app, name="search")

if __name__ == "__main__":
    app()
