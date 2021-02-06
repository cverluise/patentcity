# CARD

## ℹ️ Model Overview

|||
|---|---|
|Name| `de_ent_ddpatent01` & `de_ent_ddpatent02` |
|Language|German (de)|
|Pipeline|ner |
|Authors|Bergeaud and Verluise|
|Date (last)|02/2021 |
|License|MIT|


## 👷 Training

```shell
FORMAT=ddpatent01  # ddpatent02
spacy train configs/de_t2vner.cfg --paths.train data/train_ent_${FORMAT}.spacy --paths.dev data/train_ent_${FORMAT}.spacy --output models/de_ent_${FORMAT}
```

## 🔮 Model Performance

### `de_ent_ddpatent01/model-best`

|    |   ALL |   ASG |   INV |   LOC |   OCC |
|:---|------:|------:|------:|------:|------:|
| p  |  0.99 |  0.99 |  0.96 |  0.99 |  0.99 |
| r  |  0.99 |  0.99 |  0.96 |  0.99 |  1    |
| f  |  0.99 |  0.99 |  0.96 |  0.99 |  0.99 |

### `de_ent_ddpatent02/model-best`

|    |   ALL |   ASG |   INV |   LOC |   OCC |
|:---|------:|------:|------:|------:|------:|
| p  |  0.95 |  0.94 |  0.95 |  0.98 |  0.94 |
| r  |  0.94 |  0.87 |  0.97 |  0.95 |  0.94 |
| f  |  0.95 |  0.91 |  0.96 |  0.96 |  0.94 |


## 🎯 Intended use

`de_ent_ddpatent0*` have been specifically trained on DD patents. The model's performance are not guaranteed out of this scope.

### 🔂 Versions and alternative approaches

|Version|Comment|
|---|---|
|0.1|ner - spaCy v2|
|1.0|ner - spaCy v3|
