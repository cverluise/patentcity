# :cookie: Recipe

#### Serialize data

```shell
LANG=fr
OFFICE=fr
FORMAT=frpatent01 # frpatent02
patentcity brew v1 "data_${OFFICE}/${FORMAT}/*.txt" models/${LANG}_ent_${FORMAT}/model-best configs/config_rel_best_${FORMAT}.yaml >> entrel_${FORMAT}.jsonl
```

#### Prepare data for geocoding

```shell
FORMAT=frpatentxx
# put everything together
cat entrel_frpatent*.jsonl >> entrel_${FORMAT}.jsonl

# prep data
mv entrel_${FORMAT}.jsonl entrel_${FORMAT}.jsonl_tmp && patentcity brew v1.topping entrel_${FORMAT}.jsonl_tmp >> entrel_${FORMAT}.jsonl
patentcity geo prep-geoc-data entrel_${FORMAT}.jsonl | sort -n -u >> loc_${FORMAT}_v1.txt

# get new data (only if previous geocoding round(s), here beta)
mv loc_${FORMAT}_v1.txt loc_${FORMAT}_v1.txt_tmp &&  comm -13 <(sort loc_${FORMAT}_beta.txt) <(sort loc_${FORMAT}_v1.txt_tmp) >> loc_${FORMAT}_v1.txt
# loc_frpatentxx_v1.txt is now restricted to the loc which have never been seen before (at least in beta)
```

#### HERE geocoding

> We do not use HERE for France

#### Gmaps geocoding

#### Manual correction

````shell script
patentcity utils add-geoc-disamb lib/fr_disamb.txt lib/fr_index_geoc.txt >> geoc_frpatentxx_manual.jsonl
````

#### Harmonize, combine and incorporate geocoded data

```shell script
patentcity geo add-geoc-data fr_entgeoc_frpatentxx_beta.jsonl --geoc-file fr_geoc_frpatentxx_manual.csv --source MANUAL >> fr_entgeoc_frpatentxx_beta-disamb.jsonl
```

#### Build

```shell script
bq load --source_format=NEWLINE_DELIMITED_JSON --max_bad_records=100 --ignore_unknown_values  --replace --project_id patentcity  patentcity.fr_entgeoc_patentxx gs://patentcity_dev/FR/beta/fr_entgeoc_frpatentxx_beta-disamb.jsonl.gz  schema/fr_entgeoc_lg_future.json
```
