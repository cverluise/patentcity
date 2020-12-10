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
patentcity geo prep-geoc-data ddpatentxx_beta.jsonl >> dd_locxx_beta.txt
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
patentcity geo add-geoc-data ddpatentxx_beta.jsonl --geoc-file dd_locxx_beta-geoc_here.csv --source HERE>> ddpatentxx_beta-geoc_here.jsonl
patentcity geo add-geoc-data ddpatentxx_beta-geoc_here.jsonl --geoc-file dd_locxx_beta-geoc_gmaps.csv --source GMAP >> ddpatentxx_beta-geoc_gmaps.jsonl
patentcity geo add-geoc-data ddpatentxx_beta-geoc_gmaps.jsonl --geoc-file lib/iso_geoc_manual.csv --source MANUAL >> ddpatentxx_beta-geoc.jsonl
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
