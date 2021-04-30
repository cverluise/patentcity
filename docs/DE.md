# DE

## Background

The German Patent and Trade Mark Office (DPMO) was founded in 1877. The first patent was granted as early as July 2, 1877. There was (close to) no patent published between 1945 and 1950. The 1949-1992 period is characterised by the split of Germany in two distinct countries (BDR and DDR) and consequently of the split of the patent system as well. After that date, the two offices reunified into the DPMO . We are not aware of previous research trying to extract the location of patentees filing in Germany.

We address all German patents with a publication date between 1877 and 1980 published at the DPMO. This does not include East Germany (1950-1992). We address all patents with kind-code **A1, B, B3, C, C1, D1**. In total, we consider **1,983,161** documents from 1877.


## 📚 Data

From the earliest patent that we consider DE1C to patent DE7927785 (excluded), we collected image data (png) from Espacenet and OCRed the first page using Tesseract v5.

Patent office | Time span (publication year)| Kind code(s)
---|---|---
DE|1877-1980|A1, B, B3, C, C1, D1

Publication number (range)| Data source | Pre-processing | E.g. | Format #
 --- | --- | --- | --- | ---
DE1C-DE977922C | Espacenet | OCR |DE283698C| 1
DE1000001B-DE7927785 | Espacenet | OCR | DE2454950C| 2


## 🚜 Extraction schema

See the detailed [annotation guidelines](./DE_ANNOTATION_GUIDELINES.md)

## 🔮 Model

See the detailed [model card](./DE_MODEL_CARD.md)

## Other

See the detailed [date imputation](./DE_DATE_IMPUTATION.md) documentation.
