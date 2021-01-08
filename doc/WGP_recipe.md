# Recipe

#### Load  person - location_id crossover

````shell script
bq load --replace --source_format CSV --autodetect patentcity:external.person_location_id gs://gder_dev/person_location_id.csv.gz
bq load --replace --source_format CSV --autodetect patentcity:external.inventor_applicant_location_id gs://gder_dev/inventor_applicant_location_id.csv.gz
````

#### Build Gmaps index (patent city flavor)

```shell script
patentcity utils get-gmaps-index-wgp addresses_florian45.csv >> addresses_florian45.jsonl
patentcity utils get-gmaps-index-wgp addresses_florian25.csv >> addresses_florian25.jsonl
patentcity geo harmonize-geoc-data-gmaps addresses_florian45.jsonl --out-format csv >> addresses_florian45_patentcity.csv
patentcity geo harmonize-geoc-data-gmaps addresses_florian25.jsonl --out-format csv >> addresses_florian25_patentcity.csv
````

#### Load addresses table

```shell script
bq load --replace --autodetect --source_format CSV patentcity:external.addresses_florian25_patentcity gs://gder_dev/addresses_florian25_patentcity.csv.gz
bq load --replace --autodetect --source_format CSV patentcity:external.addresses_florian45_patentcity gs://gder_dev/addresses_florian45_patentcity.csv.gz
```

#### Join

```shell script
KEY_FILE="credentials-patentcity.json"
patentcity io build-wgp-as-patentcity --addresses-table patentcity.external.addresses_florian25_patentcity --patentee-location-table patentcity.external.inventor_applicant_location_id --flavor 25 --key-file $KEY_FILE
patentcity io build-wgp-as-patentcity --addresses-table patentcity.external.addresses_florian45_patentcity --patentee-location-table patentcity.external.person_location_id --tls206-table usptobias.patstat.tls206 --tls207-table usptobias.patstat.tls207 --flavor 45 --key-file $KEY_FILE
```

#### Group by `publication_number` - format v1

<span style="color: orange; "> TODO
- Order by `publication_number` and export to GS as jsonl
- `jq 'groupby(.publication_number) | {publication_number:...}'`
</span>
