import typer
from google.cloud import bigquery
from google.oauth2 import service_account

from patentcity.utils import ok

app = typer.Typer()


def _get_bq_client(credentials):
    credentials_ = service_account.Credentials.from_service_account_file(
        credentials, scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )

    client = bigquery.Client(credentials=credentials_, project=credentials_.project_id)
    return client


def _get_job_done(
    query, destination_table, credentials, write_disposition="WRITE_TRUNCATE", **kwargs
):
    job_config = bigquery.QueryJobConfig(
        destination=destination_table, write_disposition=write_disposition, **kwargs
    )
    client = _get_bq_client(credentials)
    typer.secho(f"Start:\n{query}", fg=typer.colors.BLUE)
    client.query(query, job_config=job_config).result()

    typer.secho(
        f"{ok}Query results saved to {destination_table}", fg=typer.colors.GREEN
    )


@app.command()
def augment_patentcity(src_table: str, destination_table: str, credentials: str = None):
    """Add (mainly interoperability) variables to `src_table` and save to `destination_table

    Arguments:
        src_table: source table (project.dataset.table)
        destination_table: destination table (project.dataset.table)
        credentials: BQ credentials file path

    **Usage:**
        ```shell
        patentcity io augment-patentcity <src_table> <destination_table> credentials-patentcity.json
        ```

    """
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
    _get_job_done(query, destination_table, credentials)


@app.command()
def impute_publication_date(
    src_table: str,
    imputation_table: str,
    country_code: str = None,
    credentials: str = None,
):
    """Update `src_table` publication_date - DE & DD only

    Arguments:
        src_table: source table (project.dataset.table)
        imputation_table: imputation table (project.dataset.table)
        country_code: in ["DE", "DD"]
        credentials: BQ credentials file path

    **Usage:**
        ```shell
        patentcity io impute-publication-date <src_table> <imputation_table> --country-code DE --credentials credentials-patentcity.json
        ```
    """
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
    client = _get_bq_client(credentials)
    typer.secho(f"Start:\n{query}", fg=typer.colors.BLUE)
    client.query(query).result()

    typer.secho(f"{ok}{src_table} updated.", fg=typer.colors.GREEN)


@app.command()
def extract_sample_kepler(
    src_table: str,
    dest_file: str,
    sample_ratio: float = 0.1,
    office: str = None,
    credentials: str = None,
):
    """Extract sample for kepler.gl

    Arguments:
        src_table: source table (project.dataset.table)
        dest_file: destination file path (local)
        sample_ratio: share of patents to extract
        office: patent office two letter-code (e.g. DD, DE, FR, etc)
        credentials: BQ credentials file path

    **Usage:**
        ```shell
        patentcity io extract-sample-kepler <src_table> <dest_file> --office DE --credentials credentials-patentcity.json
        ```
    """
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
    client = _get_bq_client(credentials)
    typer.secho(f"Start:\n{query}", fg=typer.colors.BLUE)
    df = client.query(query).to_dataframe()
    df.to_csv(dest_file, index=False)
    typer.secho(f"{ok}Extract for Kepler saved to {dest_file}.", fg=typer.colors.GREEN)


@app.command()
def build_wgp_as_patentcity(
    addresses_table: str,
    patentee_location_table: str,
    patstat_patent_properties_table: str = None,
    tls206_table: str = None,
    tls207_table: str = None,
    destination_table: str = None,
    flavor: int = None,
    credentials: str = None,
):
    """Join addresses and individuals from WGP and add data at the patent as well as individual level.

    Arguments:
        addresses_table: WGP addresses table (project.dataset.table)
        patentee_location_table: WGP patentees table (project.dataset.table)
        patstat_patent_properties_table: PATSTAT patent properties table on BQ (project.dataset.table)
        tls206_table: PATSTAT tls206 table on BQ (project.dataset.table)
        tls207_table: PATSTAT tls207 table on BQ (project.dataset.table)
        destination_table: destination table (project.dataset.table)
        flavor: WGP source data flavor (in [25, 45])
        credentials: BQ credentials file path

    **Usage:**
        ```shell
        patentcity io build-wgp-as-patentcity patentcity.external.addresses_florian45_patentcity patentcity.external.person_location_id --tls206-table patentcity.external.tls206 --tls207-table patentcity.external.tls207 --patstat-patent-properties-table patentcity.external.patstat_patent_properties --destination-table patentcity.tmp.patentcity45 --flavor 45 --key-file $KEY_FILE
        ```
    """
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
    _get_job_done(query, destination_table, credentials)


@app.command()
def order(
    src_table: str,
    by: str = None,
    destination_table: str = None,
    credentials: str = None,
):
    """Order `src_table` by `by` and stage it onto `destination_table`

    Arguments:
        src_table: source table (project.dataset.table)
        by: ordering dimension (e.g. publication_number)
        destination_table: destination table (project.dataset.table)
        credentials: BQ credentials file path

    **Usage:**
        ```shell
        patentcity io order patentcity.tmp.patentcity25 --by publication_number --destination-table patentcity.tmp.tmp25 --key-file credentials-patentcity.json
        ```
    """
    query = f"""
    SELECT
      *
    FROM
      `{src_table}`
    ORDER BY
      {by}  # publication_number
    """
    _get_job_done(query, destination_table, credentials)


@app.command()
def get_stratified_sample(
    src_table: str,
    bin_size: int = 50,
    preview: bool = False,
    destination_table: str = None,
    credentials: str = None,
):
    """Return a stratified sample of `src_table` (based on country_code and publication_decade) with `bin_size` samples
    in each bin (if possible).

    Arguments:
        src_table: source table (project.dataset.table)
        bin_size: bin size
        preview: if True, output not saved and table stats to stdout. Else, output saved to `destination_table`
        destination_table: destination table (project.dataset.table)
        credentials: BQ credentials file path

    **Usage:**
        ```shell
        patentcity io get-stratified-sample patentcity.patentcity.v1
        ```

    !!! tip
        [Stratified random sampling with bigquery - StackOverflow](https://stackoverflow.com/questions/52901451/stratified-random-sampling-with-bigquery)

    """
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
      FROM `{src_table}`,  # patentcity.patentcity.wgp_v1
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
        client = _get_bq_client(credentials)
        tmp = (
            client.query(query)
            .to_dataframe()
            .sort_values(by=["country_code", "publication_decade"])
        )
        typer.echo(tmp.to_markdown(index=False))
        typer.secho(f"Nb samples: {tmp['nb_samples'].sum()}", fg=typer.colors.BLUE)
    else:
        _get_job_done(query, destination_table, credentials)


@app.command()
def get_wgp25_recid(
    country_code: str,
    src_table: str,
    patstat_patent_properties_table: str,
    destination_table: str,
    credentials: str,
):
    """Extract recId and searchText from wgp25 for patents published in `country_code`.

    Arguments:
        country_code: country code of the patent office (e.g. DE, FR, GB, US, etc)
        src_table: source table (project.dataset.table)
        patstat_patent_properties_table: PATSTAT patent properties table on BQ (project.dataset.table)
        destination_table: destination table (project.dataset.table)
        credentials: BQ credentials file path

    **Usage:**
        ```shell
        OFFICE=DE
        python patentcity/io.py get-wgp25-recid $OFFICE patentcity.external.inventor_applicant_recid patentcity.tmp.loc_${(L)OFFICE}patentwgp25 credentials-patentcity.json;
        ```

    !!! info
        This function assumes that the recId has been added to inventor_applicant_locationid beforehand (using `utils.get_recid(address_)`)."""
    assert len(country_code) == 2
    query = f"""
    WITH
      tmp AS (
      SELECT
        loc.*,
        patstat.*,
        SPLIT(patstat.publication_number, "-")[OFFSET(0)] AS country_code
      FROM
        `{src_table}` AS loc,  # patentcity.external.inventor_applicant_recid
        `{patstat_patent_properties_table}` AS patstat  # patentcity.external.patstat_patent_properties
      WHERE
        loc.appln_id = patstat.appln_id
        AND loc.appln_id IS NOT NULL
        AND SPLIT(patstat.publication_number, "-")[OFFSET(0)] IN "{country_code}"
    SELECT
      recId,
      ANY_VALUE(address_) AS searchText
    FROM
      tmp
    GROUP BY
      recId
    """
    _get_job_done(query, destination_table, credentials)


@app.command()
def family_expansion(
    src_table: str, destination_table: str, credentials: str, destination_schema: str
):
    """Expand along families in `table ref`. The returned table contains all publications belonging to a family
    existing in `src_table` *but* absent from the latter. Family data are *assigned* from data in `src_table`."""
    query = f"""
    WITH
      family_table AS (
      SELECT
        family_id,
        ANY_VALUE(patentee) as patentee
      FROM
        `{src_table}`  # patentcity.patentcity.v100rc4
     GROUP BY
      family_id   ),
      publication_list AS (
      SELECT
        DISTINCT(publication_number) AS publication_number
      FROM
        `{src_table}`),  # patentcity.patentcity.v100rc4
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
    SPLIT(expanded_family_table.publication_number, "-")[OFFSET(2)] as kind_code,
    "EXP" AS origin
    FROM
    publication_list
    RIGHT JOIN
    expanded_family_table
    ON
    expanded_family_table.publication_number=publication_list.publication_number
    WHERE publication_list.publication_number IS NULL
  """
    _get_job_done(
        query, destination_table, credentials, destination_schema=destination_schema
    )


@app.command()
def filter_kind_codes(src_table: str, destination_table: str, credentials: str):
    """Filter `src_table` to make sure that only *utility patents* are reported.

    Arguments:
        src_table: source table (project.dataset.table)
        destination_table: destination table (project.dataset.table)
        credentials: BQ credentials file path

    **Usage:**
        ```shell
        patentcity io filter-kind-codes <src_table> <destination_table> credentials-patentcity.json
        ```
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
      `{src_table}`) # patentcity.patentcity.v100rc4
    SELECT
      origin.* FROM
      `{src_table}` as origin,  # patentcity.patentcity.v100rc4
      keep_list
      WHERE
        keep_list.publication_number = origin.publication_number
        AND keep_list.keep IS TRUE
    """
    _get_job_done(query, destination_table, credentials)


if __name__ == "__main__":
    app()
