# Recipe

#### Serialize data

````shell script

````

#### Prepare data for geocoding

````shell script
patentcity geo prep-geoc-data dd_patentxx_beta.jsonl >> dd_locxx_beta.txt
patentcity utils prep-searchtext dd_locxx_beta.txt | grep "|" >> dd_locxx_beta_prep.txt
````

#### HERE geocoding

````shell script
patentcity geo post-geoc-data-here dd_locxx_beta_prep.txt $HERE_KEY deu
patentcity geo get-geoc-status-here $REQUEST_ID $HERE_KEY
patentcity geo get-geoc-data-here $REQUEST_ID $HERE_KEY
# name result dd_locxx_beta-geoc_here.csv
````

#### Gmaps geocoding

````shell script
patentcity utils get-recid-nomatch dd_locxx_beta-geoc_here.csv dd_locxx_beta_prep.txt | grep "|" >> dd_locxx_beta-nomatch_here.txt
patentcity geo get-geoc-data-gmaps  dd_locxx_beta-nomatch_here.txt $GMAPS_KEY de >> dd_locxx_beta-geoc_gmaps.jsonl
````

#### Harmonize, combine & incorporate geocoded data

```shell script
#Harmonize (Gmaps-> HERE)
patentcity geo harmonize-geoc-data-gmaps dd_locxx_beta-geoc_gmaps.jsonl --out-format csv >> dd_locxx_beta-geoc_gmaps.csv

#Combine
#cat dd_locxx_beta-geoc_here.csv | grep -v NOMATCH >> dd_locxx_beta-geoc_xx.csv && cat dd_locxx_beta-geoc_gmaps.csv >> dd_locxx_beta-geoc_xx.csv

#Incorporate
patentcity geo add-geoc-data dd_patentxx_beta.jsonl --geoc-file dd_locxx_beta-geoc_here.csv --source HERE>> dd_patentxx_beta-geoc_here.jsonl
patentcity geo add-geoc-data dd_patentxx_beta-geoc_here.jsonl --geoc-file dd_locxx_beta-geoc_gmaps.csv --source GMAPS >> dd_patentxx_beta-geoc_gmaps.jsonl
patentcity geo add-geoc-data dd_patentxx_beta-geoc_gmaps.jsonl --geoc-file lib/iso_geoc_manual.csv --source MANUAL >> dd_patentxx_beta-geoc.jsonl
rm dd_patentxx_beta-geoc_here.jsonl dd_patentxx_beta-geoc_gmaps.jsonl
```

#### Build

````shell script
bq load --source_format=NEWLINE_DELIMITED_JSON --max_bad_records=100 --ignore_unknown_values --replace patentcity:patentcity.dd_entgeoc_patentxx gs://patentcity_dev/DD/beta/dd_patentxx_beta-geoc.jsonl schema/dd_entgeoc_lg_future.json

# Augment dataset
patentcity io augment-patentcity patentcity.patentcity.dd_entgeoc_patentxx patentcity.patentcity.dd_entgeoc_patentxx_conso --key-file credentials-patentcity.json

# Impute missing publication_date - DE only
patentcity utils expand-pubdate-imputation lib/dd_publication_date_imputation.csv --output lib/dd_publication_date_imputation_expanded.csv
bq load --source_format=CSV  --max_bad_records=1 tmp.dd_pubdate_imputation lib/dd_publication_date_imputation_expanded.csv schema/de_pubdate_imputation.json
patentcity io impute-publication-date patentcity.patentcity.dd_entgeoc_patentxx_conso patentcity.tmp.dd_pubdate_imputation --key-file credentials-patentcity.json
````
