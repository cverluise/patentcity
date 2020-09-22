import typer
import patentcity_geo
import patentcity_brew
import patentcity_utils
import patentcity_io

app = typer.Typer()

app.add_typer(patentcity_geo.app, name="geo")
app.add_typer(patentcity_brew.app, name="brew")
app.add_typer(patentcity_io.app, name="io")
app.add_typer(patentcity_utils.app, name="utils")


if __name__ == "__main__":
    app()
