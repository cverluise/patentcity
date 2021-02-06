# CARD


## ℹ️ Model Overview

|||
|---|---|
|Name|`fr_ent_frpatent01` & `fr_ent_frpatent02` |
|Language|French (fr)|
|Pipeline|ner |
|Authors|Bergeaud and Verluise|
|Date (last)|02/2021 |
|License|MIT|

## 👷 Training

```shell
FORMAT=frpatent01  # frpatent02
spacy train configs/fr_t2vner.cfg --paths.train data/train_ent_${FORMAT}.spacy --paths.dev data/train_ent_${FORMAT}.spacy --output models/de_ent_${FORMAT}
```

## 🔮 Model performance


### `fr_ent_frpatent01/model-best`

|    |   ALL |   ASG |   CLAS |   INV |   LOC |
|:---|------:|------:|-------:|------:|------:|
| p  |  0.97 |  0.99 |   0.93 |  0.99 |  0.99 |
| r  |  0.97 |  0.99 |   0.93 |  1    |  0.99 |
| f  |  0.97 |  0.99 |   0.93 |  0.99 |  0.99 |


### `fr_ent_frpatent02/model-best`

|    |   ALL |   ASG |   INV |   LOC |
|:---|------:|------:|------:|------:|
| p  |  0.98 |  0.98 |  0.99 |  0.99 |
| r  |  0.98 |  0.98 |  0.98 |  0.99 |
| f  |  0.98 |  0.98 |  0.98 |  0.99 |


## 🎯 Intended use

`en_ent_frpatent0*` have been specifically trained on FR patents (resp FR317502A-FR1569050A and FR1605567A-FR2427761A). The model's performance are not guaranteed out of this scope.

## 🔂 Versions and alternative approaches

|Version|Comment|
|---|---|
|0.1|ent - v2 spaCy|
|1.0|ent - v3 spaCy|


## References


- [EspaceNet] [EspaceNet Patent Search](https://www.epo.org/searching-for-patents/technical/espacenet.html), EPO
- Tesseract, 2014-2020, https://github.com/tesseract-ocr/tesseract/

## Notes

This document is based on:

- [Data descriptor format](https://www.nature.com/sdata/publish/for-authors#format), Nature of Scientific Data
- [FAIR principles](https://www.go-fair.org/fair-principles/)
- [Spacy models description](https://spacy.io/models/en)
- [Model cards for model description, Mitchell et al, 2019](https://arxiv.org/pdf/1810.03993.pdf)
