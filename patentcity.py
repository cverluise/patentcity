import typer
import patentcity_geo
import patentcity_brew
import patentcity_utils

app = typer.Typer()

app.add_typer(patentcity_geo, name="geo")
app.add_typer(patentcity_brew, name="brew")
app.add_typer(patentcity_utils, name="utils")
