# CARD


## ℹ️ Model Overview

|||
|---|---|
|Name| `de_ent_depatent01` & `de_ent_depatent02` |
|Language|German (de)|
|Pipeline|ner |
|Authors|Bergeaud and Verluise|
|Date (last**)|02/2020 |
|License|MIT|


## 👷 Training

```shell
FORMAT=depatent01  # depatent02
spacy train configs/de_t2vner.cfg --paths.train data/train_ent_${FORMAT}.spacy --paths.dev data/train_ent_${FORMAT}.spacy --output models/de_ent_${FORMAT}
```

## 🔮 Model Performance

### `de_ent_depatent01/model-best`

|    |   ALL |   ASG |   CLAS |   INV |   LOC |   OCC |
|:---|------:|------:|-------:|------:|------:|------:|
| p  |  0.99 |  0.98 |   0.99 |  0.99 |     1 |  0.97 |
| r  |  0.99 |  0.99 |   1    |  0.96 |     1 |  0.98 |
| f  |  0.99 |  0.98 |   1    |  0.98 |     1 |  0.97 |


### `de_ent_depatent02/model-best`

|    |   ALL |   ASG |   CIT |   CLAS |   INV |   LOC |   OCC |
|:---|------:|------:|------:|-------:|------:|------:|------:|
| p  |  0.99 |  0.99 |     0 |   0.99 |  0.98 |  0.99 |  0.97 |
| r  |  0.98 |  0.98 |     0 |   1    |  0.99 |  0.98 |  0.97 |
| f  |  0.98 |  0.98 |     0 |   0.99 |  0.99 |  0.98 |  0.97 |


## 🎯 Intended use

`de_ent_depatent0*_sm` have been specifically trained on DE patents (resp DE1C-DE977922C and DE1000001B-). The model's performance are not guaranteed out of this scope.



## 🔂 Versions and alternative approaches

|Version|Comment|
|---|---|
|0.1|ner - spaCy v2|
|1.0|ner - spaCy v3|
