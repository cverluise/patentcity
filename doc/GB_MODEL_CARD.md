# CARD

## Background and summary

Although evidence of an earlier version of patents can be found in 1449, the British patent system starts in 1623 (Plasseraud and Savignon, 1983). There were no official publications prior to 1852. To our knowledges, most patent publications earlier than 1894 have not been digitalized, and some are still missing from 1894 to 1900.

We consider all patents with a publication date between 1894 and 1980. We address all patents with kind-code A. In total, we consider 1,780,385 documents from 1894.


## Data source


From the earliest patent that we consider GB189317126A to patent GB2000001A (excluded), we collected image data (png) from Espacenet and OCRed the first page using Tesseract v5.


Publication number (range)| Data source | Pre-processing | E.g. | Format #
 --- | --- | --- | --- | ---
GB189317126A-GB2000001A (excluded) | Espacenet | OCR | GB309428A| 1
GB2000001A-GB2023380A | Espacenet | OCR | GB2016002A| 2



## Model descriptionMM

### 🚜 Extraction Schema

We extract 5 different "entities" from GB patents:

Entity|Content|E.g.
---|---|---
`PERS`| Person full name | <font style="border:2px solid red">Maxim Hanson Hersey `PERS`</font>, Lighting Engineer
`ORG`| Firm full name | We, <font style="border:2px solid blue">The Convex Incandescent Mantle Company Limited `ORG`</font>, Manufacturers
`CIT`| The origin of the firm or citizenship of the person | a <font style="border:2px solid yellow">subject of the king of Freat Britain and Ireland `CIT`</font>,
`LOC`| Location of the person/firm| Maxim Hanson Hersey, Lighting Engineer, of <font style="border:2px solid green">145, Bethune Road, Amhurst Park, London N. `LOC`</font>.
`OCC`| Occupation of the person | Maxim Hanson Hersey, <font style="border:2px solid magenta">Lighting Engineer `OCC`</font>.

Entities are tied together with 3 types of relations.

Relation|Content|E.g.
---|---|---
`CITIZENSHIP`| Links an `ORG`/`PERS` to its `CIT` | <font style="border:2px solid red">Maxim Hanson Hersey `PERS`</font><font color="red">--</font>`CITIZENSHIP`<font color="yellow">--></font><font style="border:2px solid yellow">subject of the king of Great Britain and Ireland `CIT`</font>
`LOCATION`|Links an `ORG`/`PERS` to its `LOC` | <font style="border:2px solid red">Maxim Hanson Hersey `PERS`</font><font color="red">--</font>`LOCATION`<font color="green">--></font><font style="border:2px solid green">145, Bethune Road, Amhurst Park, London N. `LOC`</font>
`OCCUPATION`|Links an `PERS` to its `OCC`| <font style="border:2px solid red">Maxim Hanson Hersey `PERS`</font><font color="red">--</font>`OCCUPATION`<font color="magenta">--></font><font style="border:2px solid magenta">Lighting Engineer `OCC`</font>


### ℹ️ Model Overview

|||
|---|---|
|Name|`en_ent_gbpatent01_sm`|
|Language|English |
|Pipeline|ner |
|Authors|Bergeaud and Verluise|
|Date|10/2020 |
|License|MIT|


### 👷 Training

```python
spacy train en models/en_ent_gbpatent01_sm/ data/train_ent_gbpatent01.json data/test_ent_gbpatent01.json -p ner --version 0.1
```

Nb: we keep only the `model-best

### 🔮 Model Performance

-|ORG|CIT|LOC|OCC| PERS | ALL
---|---|---|---|---|---|---
p|86.21|94.24|85.11|87.88|89.42|88.53
r|86.96|91.20|84.55|81.31|83.97|86.14
f|86.58|92.70|84.83|84.47|86.61|87.32


### :dart: Intended use


`en_ent_gbpatent01_sm` has been specifically trained on GB patents GB189317126A to GB2000001A (excluded). It currently supports 5 labels `PERS`, `ORG`, `CIT`, `LOC` and `OCC` (see above for more). The model's performance are not guaranteed out of this scope.


### 🔂 Versions and alternative approaches

|Version|Comment|
|---|---|
|0.1|ent|


***

## References

- Yves Plasseraud and François Savignon, "Genèse du droit unioniste des brevets", Paris, 1883
- Tesseract, 2014-2020, https://github.com/tesseract-ocr/tesseract/
- [EspaceNet] [EspaceNet Patent Search](https://www.epo.org/searching-for-patents/technical/espacenet.html), EPO

## Acknowledgements

This document is based on:

- [Data descriptor format](https://www.nature.com/sdata/publish/for-authors#format), Nature of Scientific Data
- [FAIR principles](https://www.go-fair.org/fair-principles/)
- [Spacy models description](https://spacy.io/models/en)
- [Model cards for model description, Mitchell et al. (2019](https://arxiv.org/pdf/1810.03993.pdf))
