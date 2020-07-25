# PatentCity

*Collect data from early-aged patents*

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

### Extraction models in practice

> This section says (code snippets) how to:

>- Download the model (presumably available through release)
>- Load the model
>- Extract NER and DEP


### Project structure and conventions

:ballot_box_with_check: Structure

Each folder is named after the name of the country office.

Each folder contains the following elements:

- `ANNOTATION_GUIDELINES.md` reports the annotation guidelines used for creating the gold dataset.
- `train/dev_type_ccgenrexx.json` are spaCy json files for training/evaluating the information extraction model.
- `CARD.md` reports everything you need to know about the country-specific extraction model(s) and related dataset.
- `ll_type_ccgenrexx_vv` is the spaCy information extraction model.

```text
.
├── XX/
│   ├── ANNOTATION_GUIDELINES.md
│   ├── CARD.md
│   ├── gold_cc_type_genrexx.json
│   └── ll_cc_type_genrexx_size_vv/
├── ...

```

:ballot_box_with_check: Naming conventions


Name| Short| Description
---|---|---
language | `ll` | [ISO2 language code](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2)
country |`cc` | [ISO2 country code](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2)
type	| `type` | model capabilities (e.g. core for general-purpose model with vocabulary, syntax, entities and word vectors, or depent for only vocab, syntax and entities.)
genre |	`genre` | type of text the model is trained on (e.g. web for web text, news for news text, gbpatent for patent from the GB Patent Office, etc)

See [Spacy/issues#1010](https://github.com/explosion/spaCy/issues/1010).

### TODO

- [ ] Prepare input so as to send unique addresses to batch geocoding API only

## User Guide

### :woman_scientist: Quickstart

> This section says how to:

>- Download the data
>- Start with the data. E.g. Refer to README.md

### 🔀 Interoperability

> How the dataset can be merged with other dataset. E.g. `publication_number`

### ❓Ask questions, raise issues

> General comments on raising issues, asking for feature and contributing. Ref to `CONTRIBUTING.md` for more
