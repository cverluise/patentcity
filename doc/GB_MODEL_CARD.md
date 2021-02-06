# CARD

## ℹ️ Model Overview

|||
|---|---|
|Name|`en_ent_gbpatent01`|
|Language|English |
|Pipeline|ner |
|Authors|Bergeaud and Verluise|
|Date (last)|02/2021 |
|License|MIT|


## 👷 Training

```shell
spacy train configs/en_t2vner.cfg --paths.train data/train_ent_gbpatent01.spacy --paths.dev data/train_ent_gbpatent01.spacy --output models/de_ent_gbpatent01
```

## 🔮 Model Performance

-|ORG|CIT|LOC|OCC| PERS | ALL
---|---|---|---|---|---|---
p|86.21|94.24|85.11|87.88|89.42|88.53
r|86.96|91.20|84.55|81.31|83.97|86.14
f|86.58|92.70|84.83|84.47|86.61|87.32


## :dart: Intended use


`en_ent_gbpatent01` has been specifically trained on GB patents GB189317126A to GB2000001A (excluded). The model's performance are not guaranteed out of this scope.


## 🔂 Versions and alternative approaches

|Version|Comment|
|---|---|
|0.1|ent - v2 spaCy|
