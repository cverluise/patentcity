# PatentCity

*Innovation across ages*

***

## Developer guide

### Installation and set-up


:ballot_box_with_check: Clone repo

```shell script
git clone https://github.com/Antoberge/patentcity.git

```

:ballot_box_with_check: Install dependencies

```shell script
cd patentcity/
poetry install
```

[Install poetry](https://python-poetry.org/) if needed.


:ballot_box_with_check: Install pre-commit (dev-only)

```shell script
pre-commit install
```

[Install pre-commit](https://pre-commit.com) if needed.

:ballot_box_with_check: get data & models (dev-only)

```shell script
dvc pull
```

Install [dvc](https://dvc.org/) if needed.

### Models usage

> This section says (code snippets) how to:

>- Load the model
>- Extract NER ~and DEP~~

### Recipes

#### Serialize data

````shell script

````

#### Prepare data for geocoding

````shell script

````

#### HERE geocoding

````shell script
patentcity geo post-geoc-data-here dd_locxx_beta.txt $KEY deu
patentcity geo get-geoc-status-here $REQUEST_ID $KEY
patentcity geo get-geoc-data-here $REQUEST_ID $KEY
````

#### Gmaps geocoding

````shell script
# Get HERE NOMATCH

````

#### Harmonize, combine & incorporate geocoded data

```shell script
#Harmonize (Gmaps-> HERE)
patentcity geo harmonize-geoc-data-gmaps de_locxx_beta-geoc_gmaps_sm_nopostcode.jsonl --out-format csv >> de_locxx_beta-geoc_gmaps_sm_nopostcode.csv
patentcity geo harmonize-geoc-data-gmaps de_locxx_beta-geoc_gmaps_sm_postcode.jsonl --out-format csv >> de_locxx_beta-geoc_gmaps_sm_postcode.csv

#Combine
cat data_tmp/de_locxx_beta-geoc_here_sm_nopostcode.csv | grep -v NOMATCH >> data_tmp/de_locxx_beta-geoc_sm.csv
cat data_tmp/de_locxx_beta-geoc_gmaps_sm_nopostcode.csv >> data_tmp/de_locxx_beta-geoc_sm.csv
cat data_tmp/de_locxx_beta-geoc_gmaps_sm_postcode.csv >> data_tmp/de_locxx_beta-geoc_sm.csv

#Incorporate
python patentcity.py geo add-geoc-data de_patentxx_beta_sm.jsonl --geoc-file de_locxx_beta-geoc_sm.csv >>de_patentxx_beta-geoc_sm.jsonl
```

#### Build

````shell script
bq load --source_format=NEWLINE_DELIMITED_JSON --max_bad_records=100 --ignore_unknown_values patentcity.de_entgeoc_patentxx_sample gs://patentcity_dev/DE/beta/de_patentxx_beta-geoc_sm.jsonl schema/de_entgeoc_lg_future.json

# Augment dataset
python patentcity.py io augment-patentcity patentcity.patentcity.de_entgeoc_patentxx_sample patentcity.patentcity.de_entgeoc_patentxx_sample_conso --key-file credentials-patentcity.json

# Impute missing publication_date - DE only
bq load --source_format=CSV  --max_bad_records=1 tmp.de_pubdate_imputation lib/de_publication_date_imputation_expanded.csv schema/de_pubdate_imputation.json
python patentcity.py io impute-publication-date patentcity.patentcity.de_entgeoc_patentxx_sample_conso patentcity.tmp.de_pubdate_imputation --key-file credentials-patentcity.json
````

### Everything you need to know

#### Docs

Each family of models is documented in 2 documents:

- `ANNOTATION_GUIDELINES.md` reports the annotation guidelines used for creating the gold dataset.
- `CARD.md` reports everything you need to know about the country-specific extraction model(s) and related dataset.


#### Naming conventions

The naming conventions are used both for data and models.

Name| Short| Description
---|---|---
language | `ll` | [ISO2 language code](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2)
country |`cc` | [ISO2 country code](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2)
type	| `type` | model capabilities (e.g. core for general-purpose model with vocabulary, syntax, entities and word vectors, or depent for only vocab, syntax and entities.)
genre |	`genre` | type of text the model is trained on (e.g. web for web text, news for news text, gbpatent for patent from the GB Patent Office, etc)

See [Spacy/issues#1010](https://github.com/explosion/spaCy/issues/1010).

### TODO

- [x] Prepare input so as to send unique addresses to batch geocoding API only
- [ ] Migrate :de: and :gb: to md5 (rather than adler32)
- [ ] Make schema for consolidated table
- [ ] Relationship prediction models

## User Guide

### :woman_scientist: Quickstart

> This section says how to:

>- Download the data
>- Start with the data. E.g. Refer to README.md

### 🔀 Interoperability

> How the dataset can be merged with other dataset. E.g. `publication_number`

### ❓Ask questions, raise issues

> General comments on raising issues, asking for feature and contributing. Ref to `CONTRIBUTING.md` for more
