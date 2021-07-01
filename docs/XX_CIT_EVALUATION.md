# CITIZENSHIP

## Problem

The `CIT` text extracted from the text is just a span of natural language (e.g. "a citizen of the United States"). This cannot be used as such.

## Approach

We use a Finite State Transducer. The task of the Finite State Transducer is to map these spans to a well-defined set of codes, here the ISO-3 code of the country of citizenship (e.g. USA). Below we evaluate the FST on US and GB data. Note: since there is no "learning" in the FST, overfitting is not really an issue and we do not distinguish between the training and the test set.

## Results

Data|Accuracy with fuzzy-match| Accuracy w/o no fuzzy-match
---|---|---
`gold_cit_gbpatentocr01.csv`| **98.50%** | 98.25%
`gold_cit_uspatentocr01.csv` | **98.94%** | 95.21%
`gold_cit_uspatentocr02.csv` | **93.40%** | 84.49%
`gold_cit_uspatentocr03.csv` | **92.31%** | 90.60%

In all cases, the fuzzy-match improves the overall FST accuracy.

!!! snippet
    ```shell
    # Eval on gold_cit_uspatentocr03.csv
    python patentcity/eval.py cit-fst data/gold_cit_uspatentocr03.csv --fst-file lib/cit_fst.json --verbose
    ```

## Error analysis

###  `gold_cit_gbpatentocr01.csv`

|     | publication\_number   | text                                                                | gold   | pred   | res   |
|----:|:---------------------|:--------------------------------------------------------------------|:-------|:-------|:------|
|  54 | GB-1107922-A         | Corporation organized.                                              |        | NIU    | False |
|  66 | GB-1124610-A         | citizens of the Federal -Republic of Germany                        | DDR    | DEU    | False |
|  67 | GB-1127891-A         | limited liability Company                                           |        | OMN    | False |
|  72 | GB-1138246-A         | Corporation organised and existing under the laws of the S          | USA    | NIU    | False |
| 242 | GB-1474266-A         | British subject and New Zealand citizen                             | NZL    | GBR    | False |
| 320 | GB-204013-A          | company incorporated under the laws of ureat Britain and Ireland    | GBR    | IRL    | False |
| 422 | GB-362896-A          | Limited Liability Company                                           |        | OMN    | False |
| 442 | GB-391456-A          | corporation organized and In                                        |        | NIU    | False |
| 471 | GB-429108-A          | subject of the King of Great                                        | GBR    |        | False |
| 521 | GB-508540-A          | Corporation organized deep achi under the laws of the State of West | USA    | NIU    | False |
| 726 | GB-859666-A          | corporation organized and existing under the laws of the  </p>      |        | NIU    | False |
| 774 | GB-950313-A          | corporation organized the operative magnification ratio.            |        | NIU    | False |

### `gold_cit_uspatentocr01.csv`

|     | publication\_number   | text                               | gold   | pred   | res   |
|----:|:---------------------|:-----------------------------------|:-------|:-------|:------|
|  80 | US-00832896-A1       | CORPORATION OF, NEV                | USA    |        | False |
| 103 | US-01047532-A1       | CORPORATION OF NEW                 | USA    |        | False |
| 173 | US-01485740-A1       | CORPORATION OF NEW                 | USA    |        | False |
| 193 | US-01208544-A1       | citizen of the United              | USA    | NIU    | False |
| 386 | US-00330257-A1       | citizen of the Dominion of Can-ada | CAN    | OMN    | False |
| 431 | US-01249770-A1       | CORPORATION OF PENNSYL-VANTA       | USA    |        | False |

### `gold_cit_uspatentocr02.csv`

|     | publication\_number   | text                         | gold   | pred   | res   |
|----:|:---------------------|:-----------------------------|:-------|:-------|:------|
|  10 | US-01731832-A1       | CORPORATION CF. OTLIO        | USA    | LAO    | False |
|  14 | US-01757421-A1       | CORPORATION OF CONNECTI-     | USA    |        | False |
|  64 | US-01740886-A1       | COR-PORATION OF GEORGIA      | USA    | GEO    | False |
|  67 | US-01659670-A1       | CORPORATION OF ILLI-" NOIS   | USA    |        | False |
| 112 | US-01838948-A1       | CORPORATION OF MICHI         | USA    |        | False |
| 125 | US-01677149-A1       | CORPORATION OF NEW           | USA    |        | False |
| 126 | US-01879349-A1       | CORPORATION OF NEW 7         | USA    |        | False |
| 177 | US-01777067-A1       | CORPORATION OF NEW" JERSEY   | USA    | JEY    | False |
| 178 | US-01911978-A1       | CORPORATION OF NEW. JERSEY   | USA    | JEY    | False |
| 179 | US-01630895-A1       | CORPORATION OF NEW. JERSEY   | USA    | JEY    | False |
| 180 | US-01859075-A1       | CORPORATION OF NEW. YORE     | USA    |        | False |
| 185 | US-01756906-A1       | CORPORATION OF NEWYORE       | USA    |        | False |
| 188 | US-01717493-A1       | CORPORATION OF OFTO          | USA    |        | False |
| 223 | US-01598039-A1       | CORPORATION OF PENN-         | USA    |        | False |
| 237 | US-01666523-A1       | CORPORATION OF PENNSYL-VANTA | USA    |        | False |
| 238 | US-01914412-A1       | CORPORATION OF PENNSZL-VANTA | USA    |        | False |
| 239 | US-01704180-A1       | CORPORATION OF RHODEISLAND   | USA    | LAO    | False |
| 243 | US-01608767-A1       | CORPORATION OF THAAS         | USA    | THA    | False |
| 249 | US-01717172-A1       | CORPORATION OF WIs-~CONSIN   | USA    |        | False |
| 284 | US-01694877-A1       | CORPORATIONYORK              | USA    |        | False |


### `gold_cit_uspatentocr03.csv`

|    | publication\_number   | text                        | gold   | pred   | res   |
|---:|:---------------------|:----------------------------|:-------|:-------|:------|
|  7 | US-02344331-A1       | corporation of Cali-        | USA    | MLI    | False |
| 42 | US-02437791-A1       | corporation of Hlinois      | USA    |        | False |
| 59 | US-02905903-A1       | corporation of Mlinois      | USA    | MLI    | False |
| 60 | US-03012554-A1       | corporation of New          | USA    |        | False |
| 78 | US-02226153-A1       | corporation of New. Jersey  | USA    | JEY    | False |
| 80 | US-02169128-A1       | corporation of Penn-        | USA    |        | False |
| 81 | US-02853443-A1       | corporation of Pennsyivania | USA    | IRN    | False |
| 85 | US-02992650-A1       | corporation of Ulinois      | USA    |        | False |
| 98 | US-02870832-A1       | corporation ofIilinois      | USA    | FJI    | False |
