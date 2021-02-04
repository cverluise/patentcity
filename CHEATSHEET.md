# CHEATSHEET

## Compressing prodigy gold .jsonl (from `prodigy db-out`)

> ℹ️ When exporting ENT annotated data using `prodigy db-out <dataset>`, annotations belonging to the same text are not merged, causing issues when you want to use the data for another task (e.g. correction or REL annotation). The below recipe takes care to do the merge.

```shell
FILE=""  # should be a .jsonl
mv ${FILE} ${FILE}_tmp && cat ${FILE}_tmp | grep -v '"spans":\[\]' | grep spans |jq  -s -c 'group_by(.publication_number)[] | { publication_number: .[0].publication_number, spans:[.[].spans[]]}' >> ${FILE}
```

## Head-child switch

> ℹ️ Original REL arc labelling convention went from attributes (e.g. `LOC`, `CIT`, `OCC`) to  patentees (`ASG`, `INV`), which was counter-intuitive in terms of `head` `child` and performance metrics (although) tractable. The below recipe makes the switch between head and child to make downstream REL handling easier.

```shell
for file in $(ls gold_rel_*.jsonl); do  sed 's/\"child/$tmp/g;s/\"head/\"child/g;s/$tmp/\"head/g' ${file} >> ${file}_corr; done;
```
