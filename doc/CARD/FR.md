# CARD


## Background

The patent system was institutionalised in France as early as 1791. However, the French patents published before 1900 have not been made publicly available in a digitised format. Note that the French INPI has manually built a database of inventors' locations spanning over the 19th century. This database is however not publicly available. We are not aware of prior work trying to constitute a database of the location of patentees filing in France for the 1900-1980 period.

We consider all patents with a publication date between 1900 and 1980. We address all patents with kind-code *??**. In total, we consider **??** documents from 1900.



## Data source

From the earliest patent that we consider FR317502A to patent FR2427761A (excluded), we collected image data (png) from Espacenet and OCRed the first page using Tesseract v5.


Publication number (range)| Data source | Pre-processing | E.g. | Format #
 --- | --- | --- | --- | ---
FR317502A-FR1569050A (excluded) | Espacenet | OCR |FR328212A| 1
FR1605567A-FR2427761A | Espacenet | OCR | FR1595761A| 2

## Model description

### 🚜 Extraction Schema

We extract 4 different "entities" from the header of FR patents in format category 1 and 3 in format 2.

  Entity|Content|E.g format 1 | E.g format 2
  ---|---|---|---
 `ASG`| Assignee full name | <font style="border:2px solid blue">M. Robert John Jocelyn SWAN `ASG`</font> résidant en Angleterre | Déposant: Société dite: <font style="border:2px solid blue">SALZDETFURTH A.G `ASG`</font>, résidant en République Fédérale d'Allemagne
 `INV`| Inventor full name | (Demande de brevet déposée aux Etats-Unis d'Amérique au nom de <font style="border:2px solid red"> M. Ladislas Charles MATSCH `INV`</font>) | Invention de: <font style="border:2px solid red">Takaya Endo`INV`</font>, <font style="border:2px solid red">Shui Sato`INV`</font>, <font style="border:2px solid red">Shoji Kikuchi`INV`</font>, <font style="border:2px solid red">Koichi Takabe`INV`</font>, <font style="border:2px solid red">Hiroyuki Imamura `INV`</font>, <font style="border:2px solid red">Tamotsu Kozima`INV`</font> et <font style="border:2px solid red">Tugumoto Usui `INV`</font>
	`LOC`| Location of the assignee/inventor| M. Louis LEGRAND résidant en <font style="border:2px solid green">France `LOC`</font>.| Déposant: Société dite: ROBERT BOSCH GBMH, résidant en <font style="border:2px solid green">République Fédérale d'Allemagne `LOC`</font>.
	`CLAS`| Technological class (French system) | <font style="border:2px solid purple"> XII Instruments de précision 3 POIDS ET MESURES, INSTRUMENTS DE MATHEMMATIQUES`CLAS`</font>| NR

Assignees (or inventors) and their corresponding geographic indication are tied together through the relation "LOCATION".

|Relation|Content |E.g. format 1| E.g format 2
|----|---|---|---
|`LOCATION`| Links an `ASG`/`INV` to a `LOC`  | <font style="border:2px solid blue">M.Frederic PERDRIZET `ASG`</font><font color = "blue">--</font>`LOCATION`<font color = "green">--></font><font style = "border:2px solid green">France (Gironde) `LOC`</font> | <font style="border:2px solid blue">KONISHIROKU PHOTO INDUSTRY CO LTD `ASG`</font><font color = "blue">--</font>`LOCATION`<font color = "green">--></font><font style = "border:2px solid green">Japon `LOC`</font>

See the annotation guidelines for more details.


### ℹ️ Model Overview

|||
|---|---|
|Name|`fr_ent_frpatent01_sm` & `fr_ent_frpatent02_sm` |
|Language|French |
|Pipeline|ner |
|Authors|Bergeaud and Verluise|
|Date|10/2020 |
|License|MIT|

### 👷 Training

```python
spacy train fr models/fr_ent_frpatent01_sm/ data/train_ent_frpatent01.json data/test_ent_frpatent01.json -p ner --version 0.1

spacy train fr models/fr_ent_frpatent02_sm/ data/train_ent_frpatent02.json data/test_ent_frpatent02.json -p ner --version 0.1
```

### 🔮 Model performance


#### `fr_ent_frpatent01_sm`

-|LOC|INV|ASG|CLAS|ALL
---|---|---|---|---|---
p|  97.86|  86.36|  89.57|  73.17|  88.50
r|  96.32|  88.37|  90.87|  72.00|  88.34
f|  97.08|  87.36|  90.21|  72.58|  88.42

#### `fr_ent_frpatent02_sm`
-|ASG|LOC|INV|ALL
---|---|---|---|---
p  |94.92  |98.93  |90.86| 94.99
r  |95.41  |98.40  |94.08| 96.02
f  |95.17  |98.67  |92.44| 95.50


### 🎯 Intended use

`en_ent_frpatent0*_sm` have been specifically trained on FR patents (resp FR317502A-FR1569050A and FR1605567A-FR2427761A). They support 4 (resp 3) labels `INV`, `ASG`, `LOC` and `CLAS` (`CLAS` only for `01`) . The model's performance are not guaranteed out of this scope.

### 🔂 Versions and alternative approaches

|Version|Comment|
|---|---|
|0.1|ent|


## References


- [EspaceNet] [EspaceNet Patent Search](https://www.epo.org/searching-for-patents/technical/espacenet.html), EPO
- Tesseract, 2014-2020, https://github.com/tesseract-ocr/tesseract/

## Notes

This document is based on:

- [Data descriptor format](https://www.nature.com/sdata/publish/for-authors#format), Nature of Scientific Data
- [FAIR principles](https://www.go-fair.org/fair-principles/)
- [Spacy models description](https://spacy.io/models/en)
- [Model cards for model description, Mitchell et al, 2019](https://arxiv.org/pdf/1810.03993.pdf)
