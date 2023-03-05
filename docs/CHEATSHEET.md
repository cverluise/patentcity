# CHEATSHEET

## Compressing prodigy gold .jsonl (from `prodigy db-out`)

!!! info
    When exporting ENT annotated data using `prodigy db-out <dataset>`, annotations belonging to the same text are not merged, causing issues when you want to use the data for another task (e.g. correction or REL annotation). The below recipe takes care to do the merge.

```shell
FILE=""  # should be a .jsonl
mv ${FILE} ${FILE}_tmp && cat ${FILE}_tmp | grep -v '"spans":\[\]' | grep spans |jq  -s -c 'group_by(.publication_number)[] | { publication_number: .[0].publication_number, text: .[0].text, tokens: .[0].tokens, spans:[.[].spans[]]}' >> ${FILE}
```

## Head-child switch

!!! info
    Original REL arc labelling convention went from attributes (e.g. `LOC`, `CIT`, `OCC`) to  patentees (`ASG`, `INV`), which was counter-intuitive in terms of `head`/`child` and performance metrics (although) tractable. The below recipe makes the switch between head and child to make downstream REL handling easier.

```shell
for file in $(ls gold_rel_*.jsonl); do  sed 's/\"child/$tmp/g;s/\"head/\"child/g;s/$tmp/\"head/g' ${file} >> ${file}_corr; done;
```

## Parallel models training

!!! info
    Training models takes time, it's better to train them in parallel. Don't start too many jobs at once. On a mac mini,each job takes up to 2 CPUs.

```shell
LANG=de  # support for en fr
OFFICE=de  # support dd fr gb us
cat lib/format.txt| grep $OFFICE | parallel -j 2 --eta 'spacy train configs/${LANG}_t2vner.cfg --paths.train data/train_ent_{}.spacy --paths.dev data/train_ent_{}.spacy --output models/${LANG}_ent_{}'
```

## Extract sample for kepler

```shell
OFFICE="" # e.g. DD, DE, etc
RATIO= # e.g. .2, .015
patentcity io extract-sample-kepler patentcity.patentcity.pc_v100rc1 data_tmp/sample_${OFFICE}.csv --sample-ratio ${RATIO} --office ${OFFICE} --key-file credentials-patentcity.json
```

## Extract data

```shell
RELEASE="v100rc5"
bq extract --destination_format NEWLINE_DELIMITED_JSON --compression GZIP patentcity:patentcity.${RELEASE} "gs://patentcity_dev/beta/${RELEASE}_*.jsonl.gz"
patentcity io prep-csv-extract patentcity.patentcity.${RELEASE} patentcity.stage.${RELEASE} credentials-patentcity.json
bq extract --destination_format CSV --compression GZIP patentcity:stage.${RELEASE} "gs://patentcity_dev/beta/${RELEASE}_*.csv.gz"
```
