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
    query, destination_table, key_file, write_disposition="WRITE_TRUNCATE", **kwargs
):
    job_config = bigquery.QueryJobConfig(
        destination=destination_table, write_disposition=write_disposition, **kwargs
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
def impute_publication_date(
    src_table, imputation_table, country_code: str = None, key_file: str = None
):
    """Update publication_date - DE & DD only"""
    de_clause = (
        """AND CAST(t.pubnum AS INT64)<330000""" if country_code == "DE" else """"""
    )
    query = f"""UPDATE
      `{src_table}` AS t
    SET
      t.publication_date = imputation.publication_date
    FROM
      `{imputation_table}` AS imputation
    WHERE
      t.pubnum = imputation.pubnum
      AND country_code="{country_code}"
      {de_clause}

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
    office: str = None,
    key_file: str = None,
):
    """Extract sample for kepler.gl"""
    office_clause = f"""AND country_code="{office}" """ if office else ""
    query = f"""
    SELECT
      publication_number,
      country_code,
      CAST(publication_date/10000 AS INT64) AS publication_year,
      PARSE_TIMESTAMP('%Y%m%d%H%M%S', CAST(publication_date*100000 AS STRING)) as publication_date,
      patentee.loc_country as country,
      patentee.loc_city as city,
      patentee.loc_latitude as point_latitude,
      patentee.loc_longitude as point_longitude
    FROM
      {src_table},
      UNNEST(patentee) AS patentee
    WHERE
      RAND()<{sample_ratio}
      AND publication_date>0
      AND patentee.loc_source IS NOT NULL
      AND patentee.loc_latitude IS NOT NULL
      {office_clause}
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
    patstat_patent_properties_table: str = None,
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
            patee.* EXCEPT(recId),
            loc.*,
            app_inv="INV" AS is_inv,
            app_inv="APP" AS is_app
          FROM (
            SELECT
              *
            FROM
              `{addresses_table}`  # patentcity.external.addresses_cyril25_patentcity
            WHERE
              seqNumber = 1
              AND (matchLevel="NOMATCH" AND source="HERE") IS FALSE ) AS loc
          JOIN
            `{patentee_location_table}` AS patee
            # patentcity.external.inventor_applicant_recid
          ON
            loc.recId = patee.recId )  # location_id
        SELECT
          tmp.* EXCEPT(appln_id, pat_publn_id),
          patstat.*,
          SPLIT(patstat.publication_number, "-")[OFFSET(0)] AS country_code,
          SPLIT(patstat.publication_number, "-")[OFFSET(1)] AS pubnum,
          SPLIT(patstat.publication_number, "-")[OFFSET(2)] AS kind_code
        FROM
          tmp
        LEFT JOIN
          `{patstat_patent_properties_table}` AS patstat
        ON
          tmp.pat_publn_id = patstat.pat_publn_id #tmp.appln_id = patstat.appln_id
          # here we are at the publication level, not the patent level
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
                  patee.*,
                  person.* EXCEPT(person_id)
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
              `{patstat_patent_properties_table}` AS patstat
            ON
              tmp.appln_id = patstat.appln_id
              # here we are at the the patent level
            WHERE
              SPLIT(patstat.publication_number, "-")[OFFSET(0)] IN ("DE", "GB", "FR", "US")
            """

    get_job_done(query, destination_table, key_file)


@app.command()
def order(
    table: str, by: str = None, destination_table: str = None, key_file: str = None
):
    """Order TABLE by BY and stage it to DESTINATION_TABLE (def overwrite)"""
    query = f"""
    SELECT
      *
    FROM
      `{table}`
    ORDER BY
      {by}  # publication_number
    """
    get_job_done(query, destination_table, key_file)


@app.command()
def get_stratified_sample(
    table: str,
    bin_size: int = 50,
    preview: bool = False,
    destination_table: str = None,
    key_file: str = None,
):
    """Return a stratified sample of TABLE (based on country_code and publication_decade) with BIN_SIZE samples
    (if possible) by bin. If --no-preview, then, stratified sample saved to DESTINATION_TABLE, else

    Doc: https://stackoverflow.com/questions/52901451/stratified-random-sampling-with-bigquery"""
    if preview:
        prefix = """
        SELECT COUNT(*) nb_samples, country_code, publication_decade, ROUND(100*COUNT(*)/MAX(nb_bin),2) AS percentage
        FROM (
        """
        select = (
            """SELECT publication_number, publication_decade, country_code, nb_bin"""
        )
        suffix = """) GROUP BY country_code, publication_decade"""
    else:
        prefix, select, suffix = "", "SELECT * ", ""

    query = f"""
    WITH tmp AS (
      SELECT CAST(publication_date/100000 AS INT64) AS publication_decade,
      * EXCEPT(patentee)
      FROM `{table}`,  # patentcity.patentcity.wgp_v1
            UNNEST(patentee) as patentee
        WHERE
        patentee.loc_text IS NOT NULL
        AND patentee.loc_source IS NOT NULL ),
      table_stats AS (
  SELECT *, SUM(nb_bin) OVER() AS nb_total
      FROM (
        SELECT
            country_code,
            CAST(publication_date/100000 AS INT64) AS publication_decade,
            COUNT(*) nb_bin
        FROM tmp
        GROUP BY country_code, publication_decade)
    )
    {prefix}
      {select}
      FROM tmp
      JOIN table_stats
      USING(country_code, publication_decade)
      WHERE RAND()< {bin_size}/nb_bin
    {suffix}
    """
    if preview:
        client = get_bq_client(key_file)
        tmp = (
            client.query(query)
            .to_dataframe()
            .sort_values(by=["country_code", "publication_decade"])
        )
        typer.echo(tmp.to_markdown(index=False))
        typer.secho(f"Nb samples: {tmp['nb_samples'].sum()}", fg=typer.colors.BLUE)
    else:
        get_job_done(query, destination_table, key_file)


@app.command()
def get_wgp25_recid(
    country_code: str,
    table_ref: str,
    patstat_patent_properties_table: str,
    destination_table: str,
    key_file: str,
):
    """Extract recId and searchText from wgp25 for patents published in `country_code`. Nb: assume that the recId has been added to
    inventor_applicant_locationid beforehand (using utils.get_recid(address_))."""
    assert len(country_code) == 2
    query = f"""
    WITH
      tmp AS (
      SELECT
        loc.*,
        patstat.*,
        SPLIT(patstat.publication_number, "-")[OFFSET(0)] AS country_code
      FROM
        `{table_ref}` AS loc,  # patentcity.external.inventor_applicant_recid
        `{patstat_patent_properties_table}` AS patstat  # patentcity.external.patstat_patent_properties
      WHERE
        loc.appln_id = patstat.appln_id
        AND loc.appln_id IS NOT NULL
        AND SPLIT(patstat.publication_number, "-")[OFFSET(0)] IN ("DE", "GB", "FR", "US")
    SELECT
      recId,
      ANY_VALUE(address_) AS searchText
    FROM
      tmp
    WHERE
      country_code="{country_code}"
    GROUP BY
      recId
    """
    get_job_done(query, destination_table, key_file)


@app.command()
def family_expansion(
    table_ref: str, destination_table: str, key_file: str, destination_schema: str
):
    """Expand along families in `table ref`. The returned table contains all publications belonging to a family
    existing in `table_ref` *but* absent from the latter. Family data are *assigned* from data in `table_ref`."""
    query = f"""
    WITH
      family_table AS (
      SELECT
        family_id,
        ANY_VALUE(patentee) as patentee
      FROM
        `{table_ref}`  # patentcity.patentcity.v100rc4
     GROUP BY
      family_id   ),
      publication_list AS (
      SELECT
        DISTINCT(publication_number) AS publication_number
      FROM
        `{table_ref}`),  # patentcity.patentcity.v100rc4
      expanded_family_table AS (
      SELECT
        p.publication_number,
        p.publication_date,
        family_table.*
      FROM
        `patents-public-data.patents.publications`AS p,
        family_table
      WHERE
        p.family_id = family_table.family_id
        AND family_table.family_id IS NOT NULL
        AND SPLIT(p.publication_number, "-")[OFFSET(0)] in ("DD","DE", "FR", "GB", "US"))#,

    SELECT
    expanded_family_table.*, #EXCEPT(appln_id, pat_publn_id, docdb_family_id, inpadoc_family_id),
    SPLIT(expanded_family_table.publication_number, "-")[OFFSET(0)] as country_code,
    SPLIT(expanded_family_table.publication_number, "-")[OFFSET(1)] as pubnum,
    SPLIT(expanded_family_table.publication_number, "-")[OFFSET(2)] as kind_code
    FROM
    publication_list
    RIGHT JOIN
    expanded_family_table
    ON
    expanded_family_table.publication_number=publication_list.publication_number
    WHERE publication_list.publication_number IS NULL
  """
    get_job_done(
        query, destination_table, key_file, destination_schema=destination_schema
    )


@app.command()
def filter_kind_codes(table_ref: str, destination_table: str, key_file: str):
    """Filter `table_ref` to make sure that only *utility patents* are reported. See below the precise definition of
    utility patents by country code (of the patent office).

    |Country code|Kind codes|
    |---|---|
    |DD|A, A1, A3, B|
    |DE|A1, B, B3, C, C1, D1|
    |FR|A, A1|
    |GB|A|
    |US|A (before 2001); B1,B2 (after 2001)|
    """
    query = f"""
    WITH keep_list AS (
    SELECT
      publication_number,
      CASE
        WHEN country_code = "DD" AND (kind_code in ("A", "A1", "A3", "B")) THEN TRUE
        WHEN country_code = "DE" AND (kind_code in ("A1", "B", "B3", "C", "C1", "D1")) THEN TRUE
        WHEN country_code = "FR" AND (kind_code in ("A", "A1")) THEN TRUE
        WHEN country_code = "GB" AND (kind_code in ("A")) THEN TRUE
        WHEN country_code = "US" AND (kind_code in ("A", "B1", "B2")) THEN TRUE
        ELSE FALSE
      END AS keep
    FROM
      `{table_ref}`) # patentcity.patentcity.v100rc4
    SELECT
      origin.* FROM
      `{table_ref}` as origin,  # patentcity.patentcity.v100rc4
      keep_list
      WHERE
        keep_list.publication_number = origin.publication_number
        AND keep_list.keep IS TRUE
    """
    get_job_done(query, destination_table, key_file)


if __name__ == "__main__":
    app()
