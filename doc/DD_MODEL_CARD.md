# CARD


## Background


## Data source

From the earliest patent that we consider XX to patent XX (excluded), we collected image data (png) from Espacenet and OCRed the first page using Tesseract v5.


Publication number (range)| Data source | Pre-processing | E.g. | Format #
 --- | --- | --- | --- | ---
XX | Espacenet | OCR |DE283698C| 1
XX | Espacenet | OCR | DE2454950C| 2

## Model description

### 🚜 Extraction Schema

We extract XX different "entities" from the header of DD patents in format category 1 (resp. 2).

Entity|Content|E.g format 1 | E.g. format 2
---|---|---|---
`ASG`| Assignee full name | <font style="border:2px solid blue">XX `ASG`</font> XX | <font style="border:2px solid blue">XX `ASG`</font> XX
`INV`| Inventor full name (*Erfinder*) | <font style="border:2px solid red">XX `INV`</font> XX | XX <font style="border:2px solid red">XX `INV`</font> XX
`LOC`| Location of the assignee/inventor|XX <font style="border:2px solid green">XX `LOC`</font>. | XX <font style="border:2px solid green">XX `LOC`</font>
`OCC`| Occupation of the assignee/inventor (academic title) | <font style="border:2px solid magenta">XX `OCC`</font> XX | XX <font style="border:2px solid magenta">XX `OCC`</font>XX


These entities are tied together with 2 types of relations.

| Relation | Content| E.g. format 1| E.g. format 2
|---|---|---|---
| `LOCATION`   | Links an `ASG`/`INV` to a `LOC`  | <font style="border:2px solid blue">XX `ASG`</font><font color = "blue">--</font>`LOCATION`<font color = "green">--></font><font style = "border:2px solid green">XX `LOC`</font> |<font style="border:2px solid blue">XX `ASG`</font><font color = "blue">--</font>`LOCATION`<font color = "green">--></font><font style = "border:2px solid green">XX `LOC`</font>
| `OCCUPATION` | Links an `ASG`/`INV` to an `OCC` | <font style="border:2px solid magenta">XX `OCC`</font><font color="magenta"><--</font>`OCCUPATION`<font color="blue">--</font><font style="border:2px solid blue">XX `ASG`</font> | <font style="border:2px solid blue">XX `ASG`</font><font color = "blue">--</font>`OCCUPATION`<font color = "magenta">--></font><font style="border:2px solid magenta">XX `OCC`</font>

See the annotation guidelines for more details.

### ℹ️ Model Overview

|||
|---|---|
|Name| `de_ent_ddpatent01_sm` & `de_ent_ddpatent02_sm` |
|Language|German |
|Pipeline|ner |
|Authors|Bergeaud and Verluise|
|Date|12/2020 |
|License|MIT|


### 👷 Training

```python
spacy train de models/de_ent_ddpatent01_sm/ data/train_ent_ddpatent01.json data/test_ent_ddpatent01.json -p ner --version 0.1

spacy train de models/de_ent_ddpatent02_sm/ data/train_ent_ddpatent02.json data/test_ent_ddpatent02.json -p ner --version 0.1
```

### 🔮 Model Performance

#### `de_ent_ddpatent01_sm`

-| INV| OCC| LOC| ASG | ALL
---|---|---|---|---|---
p  |75.00  |89.68  |91.97  |85.80| 87.87
r  |55.56  |96.58  |89.00  |89.87| 87.12
f  |63.83  |93.00  |90.46  |87.79| 87.49

#### `de_ent_ddpatent02_sm`

-| ASG| LOC| OCC| INV | ALL
---|---|---|---|---|---
p  |73.89  |90.32  |94.69  |86.59 | 87.87
r  |60.73  |90.86  |94.97  |91.42 | 87.22
f  |66.67  |90.59  |94.83  |88.94 | 87.55

### 🎯 Intended use

`de_ent_ddpatent0*_sm` have been specifically trained on DD patents (resp XX and XX). They support XX labels (`XX`, `XX`,...). The model's performance are not guaranteed out of this scope.

### 🔂 Versions and alternative approaches

|Version|Comment|
|---|---|
|0.1|ner|


***

## References

- [EspaceNet Patent Search](https://www.epo.org/searching-for-patents/technical/espacenet.html), EPO
- Tesseract, 2014-2020, https://github.com/tesseract-ocr/tesseract/

## Notes

This document is based on:

- [Data descriptor format](https://www.nature.com/sdata/publish/for-authors#format), Nature of Scientific Data
- [FAIR principles](https://www.go-fair.org/fair-principles/)
- [Spacy models description](https://spacy.io/models/en)
- [Model cards for model description, Mitchell et al, 2019](https://arxiv.org/pdf/1810.03993.pdf)
