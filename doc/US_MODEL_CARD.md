# CARD

## ℹ️ Model Overview

|||
|---|---|
|Name|`en_ent_uspatent01`|
|Language|English (en)|
|Pipeline|ner |
|Authors|Bergeaud and Verluise|
|Date (last)|02/2021 |
|License|MIT|


## 👷 Training

```shell
FORMAT=uspatent01  # uspatent02 uspatent03 uspatent04
spacy train configs/en_t2vner.cfg --paths.train data/train_ent_${FORMAT}.spacy --paths.dev data/train_ent_${FORMAT}.spacy --output models/de_ent_${FORMAT}
```

## 🔮 Model Performance

### `en_ent_uspatent01/model-best`

|    |   ALL |   ASG |   CIT |   INV |   LOC |
|:---|------:|------:|------:|------:|------:|
| p  |  0.98 |  0.94 |  0.98 |  1    |  0.98 |
| r  |  0.99 |  0.96 |  0.98 |  0.99 |  0.99 |
| f  |  0.99 |  0.95 |  0.98 |  0.99 |  0.99 |

### `en_ent_uspatent02/model-best`

|    |   ALL |   ASG |   CIT |   INV |   LOC |
|:---|------:|------:|------:|------:|------:|
| p  |  0.98 |  0.96 |  0.98 |     1 |  0.98 |
| r  |  0.99 |  0.96 |  0.97 |     1 |  0.99 |
| f  |  0.98 |  0.96 |  0.98 |     1 |  0.99 |


### `en_ent_uspatent03/model-best`

|    |   ALL |   ASG |   CIT |   INV |   LOC |
|:---|------:|------:|------:|------:|------:|
| p  |  0.97 |  0.96 |  0.97 |  0.99 |  0.97 |
| r  |  0.97 |  0.96 |  0.97 |  0.98 |  0.98 |
| f  |  0.97 |  0.96 |  0.97 |  0.98 |  0.98 |

### `en_ent_uspatent04/model-best`

|    |   ALL |   ASG |   INV |   LOC |
|:---|------:|------:|------:|------:|
| p  |  0.99 |  0.99 |     1 |  0.99 |
| r  |  0.99 |  0.98 |     1 |  0.99 |
| f  |  0.99 |  0.98 |     1 |  0.99 |


## :dart: Intended use

`en_ent_uspatent*` have been specifically trained on US patents. The model's performance are not guaranteed out of this scope.

## 🔂 Versions and alternative approaches

|Version|Comment|
|---|---|
|1.0|ent - v3 spaCy|
