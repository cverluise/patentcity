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


def get_job_done(
    query, destination_table, key_file, write_disposition="WRITE_TRUNCATE"
):
    job_config = bigquery.QueryJobConfig(
        destination=destination_table, write_disposition=write_disposition
    )
    client = get_bq_client(key_file)
    typer.secho(f"Start:\n{query}", fg=typer.colors.BLUE)
    client.query(query, job_config=job_config).result()

    typer.secho(
        f"{ok}Query results saved to {destination_table}", fg=typer.colors.GREEN
    )


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

    get_job_done(query, destination_table, key_file)


@app.command()
def impute_publication_date(src_table, imputation_table, key_file: str = None):
    """Update publication_date - DE & DD only"""
    query = f"""UPDATE
      `{src_table}` AS t
    SET
      t.publication_date = imputation.publication_date
    FROM
      `{imputation_table}` AS imputation
    WHERE
      t.pubnum = imputation.pubnum
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


@app.command()
def build_wgp_as_patentcity(
    addresses_table: str = None,
    patentee_location_table: str = None,
    tls206_table: str = None,
    tls207_table: str = None,
    destination_table: str = None,
    flavor: int = None,
    key_file: str = None,
):
    assert flavor in [25, 45]
    assert patentee_location_table
    assert addresses_table
    if flavor == 25:
        query = f"""

        WITH
          tmp AS (
          SELECT
            *,
            app_inv="INV" AS is_inv,
            app_inv="APP" AS is_app
          FROM (
            SELECT
              *
            FROM
              `{addresses_table}`  # patentcity.external.addresses_florian25_patentcity
            WHERE
              seqNumber = 1 ) AS loc
          JOIN
            `{patentee_location_table}` AS patee
            # patentcity.external.inventor_applicant_location_id
          ON
            loc.recId = patee.location_id )
        SELECT
          tmp.* EXCEPT(appln_id, pat_publn_id),
          patstat.*,
          SPLIT(patstat.publication_number, "-")[OFFSET(0)] AS country_code,
          SPLIT(patstat.publication_number, "-")[OFFSET(1)] AS pubnum,
          SPLIT(patstat.publication_number, "-")[OFFSET(2)] AS kind_code
        FROM
          tmp
        LEFT JOIN
          `npl-parsing.external.patstat_patent_properties` AS patstat
        ON
          tmp.appln_id = patstat.appln_id
        WHERE
          SPLIT(patstat.publication_number, "-")[OFFSET(0)] IN ("DE", "GB", "FR", "US")

        """
    if flavor == 45:
        assert tls206_table
        assert tls207_table
        query = f"""
            WITH
              tmp AS (
              WITH
                tmp_ AS (
                WITH
                  person AS (
                  SELECT
                    tls207.*,
                    tls206.person_name,
                    invt_seq_nr > 0 AS is_inv,
                    applt_seq_nr > 0 AS is_asg
                  FROM
                    `{tls206_table}` AS tls206,  # usptobias.patstat.tls206
                    `{tls207_table}` AS tls207  # usptobias.patstat.tls207
                  WHERE
                    tls207.person_id=tls206.person_id )
                SELECT
                  *
                FROM
                  `{patentee_location_table}` AS patee  # patentcity.external.person_location_id
                LEFT JOIN
                  person
                ON
                  patee.person_id = person.person_id)
              SELECT
                *
              FROM
                tmp_
              LEFT JOIN
                `{addresses_table}` AS loc  # patentcity.external.addresses_florian45_patentcity
              ON
                tmp_.location_id = loc.recId
              WHERE
                seqNumber = 1   )
            SELECT
              tmp.* EXCEPT(appln_id),
              patstat.*,
              SPLIT(patstat.publication_number, "-")[OFFSET(0)] AS country_code,
              SPLIT(patstat.publication_number, "-")[OFFSET(1)] AS pubnum,
              SPLIT(patstat.publication_number, "-")[OFFSET(2)] AS kind_code
            FROM
              tmp
            LEFT JOIN
              `npl-parsing.external.patstat_patent_properties` AS patstat
            ON
              tmp.appln_id = patstat.appln_id
            WHERE
              SPLIT(patstat.publication_number, "-")[OFFSET(0)] IN ("DE", "GB", "FR", "US")
            """

    get_job_done(query, destination_table, key_file)


if __name__ == "__main__":
    app()
