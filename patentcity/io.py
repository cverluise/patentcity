import typer
from google.cloud import bigquery
from google.oauth2 import service_account

from patentcity.utils import ok


app = typer.Typer()


def get_bq_client(key_file):
    credentials = service_account.Credentials.from_service_account_file(
        key_file, scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )

    client = bigquery.Client(credentials=credentials, project=credentials.project_id)
    return client


@app.command()
def augment_patentcity(src_table: str, destination_table: str, key_file: str = None):
    """Augment patentcity dataset. Mainly for interoperability."""
    query = f"""
    SELECT
      pc.publication_number,
      p.publication_date,
      p.family_id,
      SPLIT(pc.publication_number, "-")[OFFSET(0)] AS country_code,
      SPLIT(pc.publication_number, "-")[OFFSET(1)] AS pubnum,
      SPLIT(pc.publication_number, "-")[OFFSET(2)] AS kind_code,
      pc.* EXCEPT(publication_number)
    FROM
      `patents-public-data.patents.publications` AS p
    RIGHT JOIN
      `{src_table}` AS pc
    ON
      pc.publication_number = p.publication_number
    """
    job_config = bigquery.QueryJobConfig(
        destination=destination_table, write_disposition="WRITE_TRUNCATE"
    )
    client = get_bq_client(key_file)
    typer.secho(f"Start:\n{query}", fg=typer.colors.BLUE)
    client.query(query, job_config=job_config).result()

    typer.secho(
        f"{ok}Query results saved to {destination_table}", fg=typer.colors.GREEN
    )


@app.command()
def impute_publication_date(src_table, imputation_table, key_file: str = None):
    """Update publication_date - DE only"""
    query = f"""UPDATE
      `{src_table}` AS de
    SET
      de.publication_date = imputation.publication_date
    FROM
      `{imputation_table}` AS imputation
    WHERE
      de.pubnum = imputation.pubnum
    """
    client = get_bq_client(key_file)
    typer.secho(f"Start:\n{query}", fg=typer.colors.BLUE)
    client.query(query).result()

    typer.secho(f"{ok}{src_table} updated.", fg=typer.colors.GREEN)


@app.command()
def extract_sample_kepler(
    src_table: str,
    destination_file: str,
    sample_ratio: float = 0.1,
    key_file: str = None,
):
    """Extract sample for kepler.gl"""
    query = f"""
    SELECT
      publication_number,
      country_code,
      CAST(publication_date/10000 AS INT64) AS publication_year,
      PARSE_TIMESTAMP('%Y%m%d%H%M%S', CAST(publication_date*100000 AS STRING)) as publication_date,
      loc.country as country,
      loc.city as city,
      loc.latitude as point_latitude,
      loc.longitude as point_longitude
    FROM
      {src_table},
      UNNEST(loc) AS loc
    WHERE
      RAND()<{sample_ratio}
      AND publication_date>0
    """
    client = get_bq_client(key_file)
    typer.secho(f"Start:\n{query}", fg=typer.colors.BLUE)
    df = client.query(query).to_dataframe()
    df.to_csv(destination_file, index=False)
    typer.secho(
        f"{ok}Extract for Kepler saved to {destination_file}.", fg=typer.colors.GREEN
    )


if __name__ == "__main__":
    app()
