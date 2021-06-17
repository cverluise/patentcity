# PatentCity

*Innovation across ages*

***

## Developer guide

### Installation and set-up


```shell script
# Clone repo
git clone https://github.com/cverluise/patentcity.git

# set up env/ install dependencies and CLI
cd patentcity/
poetry install
```

[Install poetry](https://python-poetry.org/) if needed.

```shell script
# get data & models (dev-only, access to gcp bucket needed)
dvc pull
```

Install [dvc](https://dvc.org/) if needed.


### Everything you need to know

#### Docs

Each family of models is documented in 2 documents:

- `ANNOTATION_GUIDELINES.md` reports the annotation guidelines used for creating the gold dataset.
- `CARD.md` reports everything you need to know about the country-specific extraction model(s) and related dataset.


## User Guide

### :woman_scientist: Quickstart

> This section says how to:

>- Download the data
>- Start with the data. E.g. Refer to README.md

### 🔀 Interoperability

> How the dataset can be merged with other dataset. E.g. `publication_number`

### ❓Ask questions, raise issues

> General comments on raising issues, asking for feature and contributing. Ref to `CONTRIBUTING.md` for more
