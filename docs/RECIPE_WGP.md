# :cookie: Recipe

#### Load  person - location_id crossover

````shell script
bq load --replace --source_format CSV --autodetect patentcity:external.person_location_id gs://gder_dev/person_location_id.csv.gz
bq load --replace --source_format CSV --autodetect patentcity:external.inventor_applicant_location_id gs://gder_dev/inventor_applicant_location_id.csv.gz
````

#### Build Gmaps index (patent city flavor)

```shell script
patentcity utils get-gmaps-index-wgp --flavor 45 addresses_florian45.csv >> addresses_florian45.jsonl
patentcity utils get-gmaps-index-wgp --flavor 25 addresses_florian25.csv >> addresses_florian25.jsonl
patentcity geo harmonize-geoc-data-gmaps addresses_florian45.jsonl --out-format csv >> addresses_florian45_patentcity.csv
patentcity geo harmonize-geoc-data-gmaps addresses_florian25.jsonl --out-format csv >> addresses_florian25_patentcity.csv
````

#### Load addresses table

```shell script
gsutil -m cp "addresses*patentcity.csv.gz" gs://gder_dev/
bq load --replace --autodetect --source_format CSV patentcity:external.addresses_florian25_patentcity gs://gder_dev/addresses_florian25_patentcity.csv.gz
bq load --replace --autodetect --source_format CSV patentcity:external.addresses_florian45_patentcity gs://gder_dev/addresses_florian45_patentcity.csv.gz
```

#### Join

```shell script
KEY_FILE="credentials-patentcity.json"
patentcity io build-wgp-as-patentcity --addresses-table patentcity.external.addresses_florian25_patentcity --patentee-location-table patentcity.external.inventor_applicant_location_id --patstat-patent-properties-table patentcity.external.patstat_patent_properties --destination-table patentcity.tmp.patentcity25 --flavor 25 --key-file $KEY_FILE
patentcity io build-wgp-as-patentcity --addresses-table patentcity.external.addresses_florian45_patentcity --patentee-location-table patentcity.external.person_location_id --tls206-table patentcity.external.tls206 --tls207-table patentcity.external.tls207 --patstat-patent-properties-table patentcity.external.patstat_patent_properties --destination-table patentcity.tmp.patentcity45 --flavor 45 --key-file $KEY_FILE
```

#### Format data as patentcity v1

```shell script
# sort data (required since chunked at extraction)
patentcity io order patentcity.tmp.patentcity25 --by publication_number --destination-table patentcity.tmp.tmp25 --key-file credentials-patentcity.json
patentcity io order patentcity.tmp.patentcity45 --by publication_number --destination-table patentcity.tmp.tmp45 --key-file credentials-patentcity.json
# extract data
bq extract --destination_format NEWLINE_DELIMITED_JSON --compression GZIP patentcity:tmp.tmp25 "gs://tmp/flat_patentcity25_*.jsonl.gz"
bq extract --destination_format NEWLINE_DELIMITED_JSON --compression GZIP patentcity:tmp.tmp45 "gs://tmp/flat_patentcity45_*.jsonl.gz"
# remove staged tables
bq rm patentcity:tmp.tmp25
bq rm patentcity:tmp.tmp45
# download data
gsutil -m cp "gs://tmp/flat_patentcity*.jsonl.gz" ./
# nest
ls flat_patentcity25_*.jsonl.gz | cut -d_ -f 2,3 | parallel -j+0 --eta """gunzip flat_{} && jq -s -c 'group_by(.publication_number)[] | {publication_number: .[0].publication_number, publication_date: .[0].publication_date, country_code: .[0].country_code, pubnum: .[0].pubnum, kind_code: .[0].kindcode, appln_id: .[0].appln_id, family_id: .[0].docdb_family_id, patentee: [ .[] | {is_inv: .is_inv, is_asg: .is_app, loc_text: .address_, loc_recId: .recId, loc_locationLabel: .locationLabel, loc_country: .country, loc_state: .state, loc_county: .county, loc_city: .city, loc_district: .district, loc_postalCode: .postalCode, loc_street: .street, loc_building: .building, loc_houseNumber: .houseNumber, loc_longitude: .longitude, loc_latitude: .latitude, loc_matchType: .matchType, loc_matchLevel: .matchLevel, loc_seqNumber: .seqNumber} ] }' flat_{.} >> {.} && gzip {.} && gzip flat_{.}"""
ls flat_patentcity45_*.jsonl.gz | cut -d_ -f 2,3 | parallel -j+0 --eta """gunzip flat_{} && jq -s -c 'group_by(.publication_number)[] | {publication_number: .[0].publication_number, publication_date: .[0].publication_date, country_code: .[0].country_code, pubnum: .[0].pubnum, kind_code: .[0].kind_code, appln_id: .[0].appln_id, family_id: .[0].docdb_family_id, patentee: [.[] | {name_text: .person_name, person_id: .person_id, is_inv: .is_inv, is_asg: .is_asg, loc_text: .address_, loc_recId: .recId, loc_locationLabel: .locationLabel, loc_country: .country, loc_state: .state, loc_county: .county, loc_city: .city, loc_district: .district, loc_postalCode: .postalCode, loc_street: .street, loc_building: .building, loc_houseNumber: .houseNumber, loc_longitude: .longitude, loc_latitude: .latitude, loc_matchType: .matchType, loc_matchLevel: .matchLevel, loc_seqNumber: .seqNumber}]}' flat_{.} >> {.} && gzip {.} && gzip flat_{.}"""
# upload data
gsutil -m mv  "./patentcity*.jsonl.gz" gs://gder_dev/v1/
```

#### Load (BQ)

```shell script
URI="" # e.g. "gs://gder_dev/v100rc3/patentcity*.jsonl.gz"
RELEASETABLE=""  #e.g. "patentcity:patentcity.wgp_v100rc3"
bq load --source_format=NEWLINE_DELIMITED_JSON --max_bad_records=1000 --ignore_unknown_values --replace ${RELEASETABLE} ${URI} schema/patentcity_v1.sm.json
```
