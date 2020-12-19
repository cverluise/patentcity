# Recipe

#### Serialize data

#### Prepare data for geocoding

#### HERE geocoding

#### Gmaps geocoding

#### Manual correction

````shell script
patentcity utils add-geoc-disamb lib/fr_disamb.txt lib/fr_index_geoc.txt >> fr_geoc_frpatentxx_manual.jsonl
patentcity geo add-geoc-data fr_entgeoc_frpatentxx_beta-disamb.jsonl --geoc-file fr_geoc_frpatentxx_manual.csv --source MANUAL >> fr_entgeoc_frpatentxx_beta-disamb.jsonl
````

#### Harmonize, combine and incorporate geocoded data

```shell script
patentcity geo add-geoc-data fr_entgeoc_frpatentxx_beta.jsonl --geoc-file fr_geoc_frpatentxx_manual.csv --source MANUAL >> fr_entgeoc_frpatentxx_beta-disamb.jsonl
```

#### Build

```shell script
bq load --source_format=NEWLINE_DELIMITED_JSON --max_bad_records=100 --ignore_unknown_values  --replace --project_id patentcity  patentcity.fr_entgeoc_patentxx gs://patentcity_dev/FR/beta/fr_entgeoc_frpatentxx_beta-disamb.jsonl.gz  schema/fr_entgeoc_lg_future.json
```
