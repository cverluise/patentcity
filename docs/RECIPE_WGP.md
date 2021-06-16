# RECIPE WGP

!!! note
    The below snippets provide guidance for the main steps of the WGP pipeline.

## Join individuals and geocoded addresses

!!! warning
    For some reasons, the flavor 25 join yields inconsistent results. We don't know why. As a turn around, we use the addresses collected by de Rassenfosse et al (2019) but we do not use their geocoding files. We geocode the addresses ourselves.

=== "wgp45"

    ```shell
    # Load individual - location_id crossover
    bq load --replace --source_format CSV --autodetect patentcity:external.person_location_id gs://gder_dev/person_location_id.csv.gz

    # Build Geoc index (patent city flavor)
    patentcity utils get-gmaps-index-wgp --flavor 45 addresses_florian45.csv >> addresses_florian45.jsonl
    patentcity geo gmaps.harmonize addresses_florian45.jsonl --out-format csv >> addresses_florian45_patentcity.csv
    mv addresses_florian45_patentcity.csv addresses_florian45_patentcity.tmp.csv && csvstack -n source -g GMAPS addresses_florian45_patentcity.tmp.csv >> addresses_florian45_patentcity.csv
    mv addresses_florian45_patentcity.csv addresses_florian45_patentcity.tmp.csv && csvstack -n origin -g WGP45 addresses_florian45_patentcity.tmp.csv >> addresses_florian45_patentcity.csv

    # Add statistical areas
    mv addresses_florian45_patentcity.csv addresses_florian45_patentcity.tmp.csv && patentcity geo add.statisticalareas addresses_florian45_patentcity.tmp.csv "assets/statisticalareas_*.csv" >> addresses_florian45_patentcity.csv

    # Load addresses
    gzip addresses_florian45_patentcity.csv
    gsutil -m cp "addresses*patentcity.csv.gz" gs://gder_dev/
    bq load --replace --autodetect --source_format CSV  --max_bad_records 100 patentcity:external.addresses_florian45_patentcity gs://gder_dev/addresses_florian45_patentcity.csv.gz

    # Join
    KEY_FILE="credentials-patentcity.json"
    patentcity io build-wgp-as-patentcity  patentcity.external.addresses_florian45_patentcity  patentcity.external.person_location_id --tls206-table patentcity.external.tls206 --tls207-table patentcity.external.tls207 --patstat-patent-properties-table patentcity.external.patstat_patent_properties --destination-table patentcity.tmp.patentcity45 --flavor 45 --credentials $KEY_FILE
    ```

=== "wgp25 (fixed)"

    ```shell
    # Load individual - recid crossover
    # TODO add `recId` to inventor_applicant_location_id.csv >> inventor_applicant_recid.csv
    bq load --replace --source_format CSV --autodetect patentcity:external.inventor_applicant_recid gs://gder_dev/inventor_applicant_recid.csv.gz

    # Build Geoc index (patent city flavor)
    ## extract data
    for OFFICE in DE FR GB US; do
        python patentcity/io.py get-wgp25-recid $OFFICE patentcity.external.inventor_applicant_recid patentcity.tmp.loc_${(L)OFFICE}patentwgp25 credentials-patentcity.json;
        bq extract --destination_format CSV -F "|" patentcity:tmp.loc_${(L)OFFICE}patentwgp25 gs://gder_dev/loc_${(L)OFFICE}patentwgp25.txt;
    done;

    # Geocode
    ## follow the same procedure as for PatentCity see RECIPE_PATENTCITY.md
    ## harmonize HERE and GMAPS outputs
    ls geoc_*patentwgp25.gmaps.txt | cut -d. -f1,2 |parallel --eta 'patentcity geo gmaps.harmonize {}.txt --out-format csv >> {}.csv'
    ## remove extra recId field (returned by HERE)
    ls geoc_*patentwgp25.here.csv.gz | parallel --eta 'mv {} {.}.tmp.gz && csvcut -C 4 {.}.tmp.gz >> {.} && gzip {.}'

    # add source and origin
    ls geoc_*patentwgp25.here.csv.gz | parallel --eta 'mv {} {.}.tmp.gz && csvstack -n source -g HERE {.}.tmp.gz >> {.} && gzip {.}'
    ls geoc_*patentwgp25.gmaps.csv.gz | parallel --eta 'mv {} {.}.tmp.gz && csvstack -n source -g GMAPS {.}.tmp.gz >> {.} && gzip {.}'

    # pack everything together in addresses_cyril25_patentcity.csv
    zcat geoc_depatentwgp25.gmaps.csv.gz | head -n 1 >> addresses_cyril25_patentcity.csv  # this is just the header
    zcat geoc_*patentwgp25.*.csv*.gz |  grep -v "recId" | sort -u >> addresses_cyril25_patentcity.csv
    gzip addresses_cyril25_patentcity.csv

    # add origin
    mv addresses_cyril25_patentcity.csv.gz addresses_cyril25_patentcity.csv.tmp.gz && csvstack -n origin -g WGP25 addresses_cyril25_patentcity.csv.tmp.gz >> addresses_cyril25_patentcity.csv

    # Add statistical areas
    mv addresses_cyril25_patentcity.csv addresses_cyril25_patentcity.tmp.csv && patentcity geo add.statisticalareas addresses_cyril25_patentcity.tmp.csv "assets/statisticalareas_*.csv" >> addresses_cyril25_patentcity.csv
    gzip addresses_cyril25_patentcity.csv

    # Load addresses
    gsutil -m cp "addresses*patentcity.csv.gz" gs://gder_dev/
    bq load --replace --autodetect --source_format CSV  --max_bad_records 100 patentcity:external.addresses_cyril25_patentcity gs://gder_dev/addresses_cyril25_patentcity.csv.gz

    # Join
    KEY_FILE="credentials-patentcity.json"
    patentcity io build-wgp-as-patentcity  patentcity.external.addresses_cyril25_patentcity  patentcity.external.inventor_applicant_recid --patstat-patent-properties-table patentcity.external.patstat_patent_properties --destination-table patentcity.tmp.patentcity25 --flavor 25 --credentials $KEY_FILE
    ```

=== "wgp25 (broken)"

    ```shell
    # Load individual - location_id crossover
    bq load --replace --source_format CSV --autodetect patentcity:external.inventor_applicant_location_id gs://gder_dev/inventor_applicant_location_id.csv.gz

    # Build Geoc index (patent city flavor)
    patentcity utils get-gmaps-index-wgp --flavor 25 addresses_florian25.csv >> addresses_florian25.jsonl
    patentcity geo gmaps.harmonize addresses_florian25.jsonl --out-format csv >> addresses_florian25_patentcity.csv
    mv addresses_florian25_patentcity.csv addresses_florian25_patentcity.tmp.csv && csvstack -n source -g GMAPS addresses_florian25_patentcity.tmp.csv >> addresses_florian25_patentcity.csv
    mv addresses_florian25_patentcity.csv addresses_florian25_patentcity.tmp.csv && csvstack -n origin -g WGP25 addresses_florian25_patentcity.tmp.csv >> addresses_florian25_patentcity.csv

    # Load addresses
    gsutil -m cp "addresses*patentcity.csv.gz" gs://gder_dev/
    bq load --replace --autodetect --source_format CSV  --max_bad_records 100 patentcity:external.addresses_florian25_patentcity gs://gder_dev/addresses_florian25_patentcity.csv.gz

    # Join
    KEY_FILE="credentials-patentcity.json"
    patentcity io build-wgp-as-patentcity  patentcity.external.addresses_florian25_patentcity  patentcity.external.inventor_applicant_location_id --patstat-patent-properties-table patentcity.external.patstat_patent_properties --destination-table patentcity.tmp.patentcity25 --flavor 25 --credentials $KEY_FILE
    ```


## Build data

```shell
# Format data as patentcity v1
## sort data (required since chunked at extraction)
patentcity io order patentcity.tmp.patentcity25 --by publication_number --destination-table patentcity.tmp.tmp25 --credentials credentials-patentcity.json
patentcity io order patentcity.tmp.patentcity45 --by publication_number --destination-table patentcity.tmp.tmp45 --credentials credentials-patentcity.json
## extract data
gsutil -m rm "gs://tmp/flat_patentcity*.jsonl.gz"
bq extract --destination_format NEWLINE_DELIMITED_JSON --compression GZIP patentcity:tmp.tmp25 "gs://tmp/flat_patentcity25_*.jsonl.gz"
bq extract --destination_format NEWLINE_DELIMITED_JSON --compression GZIP patentcity:tmp.tmp45 "gs://tmp/flat_patentcity45_*.jsonl.gz"
## remove staged tables
bq rm patentcity:tmp.tmp25
bq rm patentcity:tmp.tmp45
## download data
gsutil -m cp "gs://tmp/flat_patentcity*.jsonl.gz" ./
## nest
ls flat_patentcity25_*.jsonl.gz | cut -d_ -f 2,3 | parallel -j+0 --eta """gunzip flat_{} && jq -s -c 'group_by(.publication_number)[] | {publication_number: .[0].publication_number, publication_date: .[0].publication_date, country_code: .[0].country_code, pubnum: .[0].pubnum, kind_code: .[0].kind_code, appln_id: .[0].appln_id, family_id: .[0].docdb_family_id, origin: .[0].origin, patentee: [ .[] | {is_inv: .is_inv, is_asg: .is_app, loc_text: .address_, loc_recId: .recId, loc_locationLabel: .locationLabel, loc_country: .country, loc_state: .state, loc_county: .county, loc_city: .city, loc_district: .district, loc_postalCode: .postalCode, loc_street: .street, loc_building: .building, loc_houseNumber: .houseNumber, loc_longitude: .longitude, loc_latitude: .latitude, loc_matchType: .matchType, loc_matchLevel: .matchLevel, loc_seqNumber: .seqNumber, loc_source: .source, loc_key: .key, loc_statisticalArea1: .statisticalArea1, loc_statisticalArea1Code: .statisticalArea1Code, loc_statisticalArea2: .statisticalArea2, loc_statisticalArea2Code: .statisticalArea2Code, loc_statisticalArea3: .statisticalArea3, loc_statisticalArea3Code: .statisticalArea3Code} ] }' flat_{.} >> {.} && gzip {.} && gzip flat_{.}"""
ls flat_patentcity45_*.jsonl.gz | cut -d_ -f 2,3 | parallel -j+0 --eta """gunzip flat_{} && jq -s -c 'group_by(.publication_number)[] | {publication_number: .[0].publication_number, publication_date: .[0].publication_date, country_code: .[0].country_code, pubnum: .[0].pubnum, kind_code: .[0].kind_code, appln_id: .[0].appln_id, family_id: .[0].docdb_family_id, origin: .[0].origin, patentee: [.[] | {name_text: .person_name, person_id: .person_id, is_inv: .is_inv, is_asg: .is_asg, loc_text: .address_, loc_recId: .recId, loc_locationLabel: .locationLabel, loc_country: .country, loc_state: .state, loc_county: .county, loc_city: .city, loc_district: .district, loc_postalCode: .postalCode, loc_street: .street, loc_building: .building, loc_houseNumber: .houseNumber, loc_longitude: .longitude, loc_latitude: .latitude, loc_matchType: .matchType, loc_matchLevel: .matchLevel, loc_seqNumber: .seqNumber, loc_source: .source, loc_key: .key, loc_statisticalArea1: .statisticalArea1, loc_statisticalArea1Code: .statisticalArea1Code, loc_statisticalArea2: .statisticalArea2, loc_statisticalArea2Code: .statisticalArea2Code, loc_statisticalArea3: .statisticalArea3, loc_statisticalArea3Code: .statisticalArea3Code}]}' flat_{.} >> {.} && gzip {.} && gzip flat_{.}"""

## upload data
gsutil -m mv  "./patentcity*.jsonl.gz" gs://gder_dev/v1/

# Load to BQ
URI="" # e.g. "gs://gder_dev/v100rc4/patentcity*.jsonl.gz"
RELEASETABLE=""  #e.g. "patentcity:patentcity.wgp_v100rc4"
bq load --source_format=NEWLINE_DELIMITED_JSON --max_bad_records=1000 --ignore_unknown_values --replace ${RELEASETABLE} ${URI} schema/patentcity_v1.sm.json
```
