# TODO: make schema for conso table

src_table = "patentcity.patentcity.de_entgeoc_patentxx_sample"
imputation_table = "patentcity.tmp.de_publication_date_imputation"
sample_ratio = 0.1


# Consolidate data (mainly interoperability)
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

# Update publication_date - DE only
query = f"""UPDATE
  `{src_table}` AS de
SET
  de.publication_date = imputation.publication_date
FROM
  `{imputation_table}` AS imputation
WHERE
  de.pubnum = imputation.pubnum
"""

# Extract sample for kepler.gl
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
"""
