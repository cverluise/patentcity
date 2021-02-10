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
FORMAT=gbpatent01
spacy train configs/en_t2vner.cfg --paths.train data/train_ent_${FORMAT}.spacy --paths.dev data/train_ent_${FORMAT}.spacy --output models/de_ent_${FORMAT}
```

## 🔮 Model Performance

### `en_ent_gbpatent01/model-best`

|    |   ALL |   ASG |   CIT |   INV |   LOC |   OCC |
|:---|------:|------:|------:|------:|------:|------:|
| p  |  0.93 |  0.93 |  0.96 |  0.95 |  0.92 |  0.9  |
| r  |  0.94 |  0.92 |  0.96 |  0.96 |  0.92 |  0.86 |
| f  |  0.94 |  0.93 |  0.96 |  0.96 |  0.92 |  0.88


## :dart: Intended use

`en_ent_gbpatent01` has been specifically trained on GB patents GB189317126A to GB2000001A (excluded). The model's performance are not guaranteed out of this scope.

## 🔂 Versions and alternative approaches

|Version|Comment|
|---|---|
|0.1|ent - v2 spaCy|
|1.0|ent - v3 spaCy|
