# CARD


## Background

The German Patent and Trade Mark Office (DPMO) was founded in 1877. The first patent was granted as early as July 2, 1877. There was (close to) no patent published between 1945 and 1950. The 1949-1992 period is characterised by the split of Germany in two distinct countries (BDR and DDR) and consequently of the split of the patent system as well. After that date, the two offices reunified into the DPMO . We are not aware of previous research trying to extract the location of patentees filing in Germany.

We address all German patents with a publication date between 1877 and 1980 published at the DPMO. This does not include East Germany (1950-1992). We address all patents with kind-code **??**. In total, we consider **??** documents from 1877.


## Data source

From the earliest patent that we consider DE1C to patent DE7927785 (excluded), we collected image data (png) from Espacenet and OCRed the first page using Tesseract v5.


Publication number (range)| Data source | Pre-processing | E.g. | Format #
 --- | --- | --- | --- | ---
DE1C-DE977922C | Espacenet | OCR |DE283698C| 1
DE1000001B-DE7927785 | Espacenet | OCR | DE2454950C| 2

## Model description

### 🚜 Extraction Schema

We extract 5 (resp. 6) different "entities" from the header of DE patents in format category 1 (resp. 2).

Entity|Content|E.g format 1 | E.g. format 2
---|---|---|---
`ASG`| Assignee full name | <font style="border:2px solid blue">ANTON KLEBER `ASG`</font> in SAARBRUCKEN | font style="border:2px solid blue">Anmelder: Greer Hydraulics, Inc. `ASG`</font>, Los Angeles, Calif. (V.St.A.)
`INV`| Inventor full name (*Erfinder*) | <font style="border:2px solid red">Frutz Doring `INV`</font>, Berlin-Frohnau ist als Erfinder genannt worden | Erfinder: <font style="border:2px solid red">Knight, David George `INV`</font> Sommershall, Chesterfield (Großbritannien)
`LOC`| Location of the assignee/inventor| Demag Akt-Ges. in <font style="border:2px solid green">Duisburg `LOC`</font>. | Anmelder: Sharp K.K., <font style="border:2px solid green">Osaka (Japan) `LOC`</font>
`OCC`| Occupation of the assignee/inventor (academic title) | <font style="border:2px solid magenta">Dipl-Ing `OCC`</font> Georg Werner Gaze, Ingolstadt | Dietrich Jurgen, <font style="border:2px solid magenta">Dr.-Ing. `OCC`</font>; 7033 Herrenberg
`CLAS`| Technological class (German system) | <font style="border:2px solid purple"> KLASSE 49h GRUPPE 27 D 16736VI/49h `CLAS`</font> | Deutsche Kl.: <font style="border:2px solid purple">42 i, 8/80 `CLAS`</font>


These entities are tied together with 2 types of relations.

| Relation | Content| E.g. format 1| E.g. format 2
|---|---|---|---
| `LOCATION`   | Links an `ASG`/`INV` to a `LOC`  | <font style="border:2px solid blue">MARIUS ALBERT de DION `ASG`</font><font color = "blue">--</font>`LOCATION`<font color = "green">--></font><font style = "border:2px solid green">PUTEAUX (Seine, Frankr.) `LOC`</font> |<font style="border:2px solid blue">The Procter&Gamble Co. `ASG`</font><font color = "blue">--</font>`LOCATION`<font color = "green">--></font><font style = "border:2px solid green">Cincinnati, Ohio (U.St.A) `LOC`</font>
| `OCCUPATION` | Links an `ASG`/`INV` to an `OCC` | <font style="border:2px solid magenta">Dr. `OCC`</font><font color="magenta"><--</font>`OCCUPATION`<font color="blue">--</font><font style="border:2px solid blue">KARL HENKEL `ASG`</font> | <font style="border:2px solid blue">Spitzke, Wolfgang `ASG`</font><font color = "blue">--</font>`OCCUPATION`<font color = "magenta">--></font><font style="border:2px solid magenta">Ing.(grad.) `OCC`</font>

See the annotation guidelines for more details.

### ℹ️ Model Overview

|||
|---|---|
|Name| `de_ent_depatent01_sm` & `de_ent_depatent02_sm` |
|Language|German |
|Pipeline|ner |
|Authors|Bergeaud and Verluise|
|Date|10/2020 |
|License|MIT|


### 👷 Training

```python
spacy train de models/de_ent_depatent01_sm/ data/train_ent_depatent01.json data/test_ent_depatent01.json -p ner --version 0.1

spacy train de models/de_ent_depatent02_sm/ data/train_ent_depatent02.json data/test_ent_depatent02.json -p ner --version 0.1
```

### 🔮 Model Performance

#### `de_ent_depatent01_sm`

-| ASG| CLAS|  LOC|  OCC| INV | ALL
---|---|---|---|---|---|---
p | 84.68 | 94.17 | 92.07 | 81.82 | 82.14  | 89.50
r | 83.33 | 91.13 | 91.13 | 81.82 | 82.14  | 87.98
f | 84.00 | 92.62 | 91.60 | 81.82 | 82.14  | 88.74

#### `de_ent_depatent02_sm`

-|CLAS    |LOC    |INV    |ASG    |OCC | ALL
---|---|---|---|---|---|---
p  |96.27  |93.13  |89.87  |90.45  |83.75  | 91.56
r  |92.81  |92.93  |92.91  |86.54  |83.75  | 91.18
f  |94.51  |93.03  |91.36  |88.45  |83.75  | 91.37


### 🎯 Intended use

`de_ent_depatent0*_sm` have been specifically trained on DE patents (resp DE1C-DE977922C and DE1000001B-). They support 5 labels `INV`, `ASG`, `LOC`, `OCC` and `CLAS` (. The model's performance are not guaranteed out of this scope.



### 🔂 Versions and alternative approaches

|Version|Comment|
|---|---|
|0.1|ner|


***

## References

- [EspaceNet] [EspaceNet Patent Search](https://www.epo.org/searching-for-patents/technical/espacenet.html), EPO
- Tesseract, 2014-2020, https://github.com/tesseract-ocr/tesseract/
## Notes

This document is based on:

- [Data descriptor format](https://www.nature.com/sdata/publish/for-authors#format), Nature of Scientific Data
- [FAIR principles](https://www.go-fair.org/fair-principles/)
- [Spacy models description](https://spacy.io/models/en)
- [Model cards for model description, Mitchell et al, 2019](https://arxiv.org/pdf/1810.03993.pdf)
