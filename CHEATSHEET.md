# CHEATSHEET

## Compressing prodigy gold .jsonl (from `prodigy db-out`)

> ℹ️ When exporting ENT annotated data using `prodigy db-out <dataset>`, annotations belonging to the same text are not merged, causing issues when you want to use the data for another task (e.g. correction or REL annotation). The below recipe takes care to do the merge.

```shell
FILE=""  # should be a .jsonl
mv ${FILE} ${FILE}_tmp && cat ${FILE}_tmp | grep -v '"spans":\[\]' | grep spans |jq  -s -c 'group_by(.publication_number)[] | { publication_number: .[0].publication_number, text: .[0].text, tokens: .[0].tokens, spans:[.[].spans[]]}' >> ${FILE}
```

## Head-child switch

> ℹ️ Original REL arc labelling convention went from attributes (e.g. `LOC`, `CIT`, `OCC`) to  patentees (`ASG`, `INV`), which was counter-intuitive in terms of `head` `child` and performance metrics (although) tractable. The below recipe makes the switch between head and child to make downstream REL handling easier.

```shell
for file in $(ls gold_rel_*.jsonl); do  sed 's/\"child/$tmp/g;s/\"head/\"child/g;s/$tmp/\"head/g' ${file} >> ${file}_corr; done;
```

## Parallel models training

> ℹ️ Training models takes time, it's better to train them in parallel

```shell
LANG=de  # support for en fr
OFFICE=de  # support dd fr gb us
cat lib/format.txt| grep $OFFICE | parallel -j 2 --eta 'spacy train configs/${LANG}_t2vner.cfg --paths.train data/train_ent_{}.spacy --paths.dev data/train_ent_{}.spacy --output models/${LANG}_ent_{}'
```

> ⚠️ Don't start too many jobs at once. On a mac mini,each job takes up to 2 CPUs.

## Train & eval REL

### Train 

```shell
# generate configs
patentcity search relationship-params configs/rel_search.yaml

# Grid search for all formats
for FORMAT in $(cat lib/formats.txt); 
do ls configs/rel_*.yaml | grep -v search | grep -v best | parallel --eta "patentcity eval relationship-model data/gold_rel_${FORMAT}.jsonl {} --report json>> {.}_${FORMAT}.json" && echo "\n## ${FORMAT}" >> doc/XX_REL_CARD.md  && patentcity search relationship-best "configs/rel_*_${FORMAT}.json" >> doc/XX_REL_CARD.md; 
done; 
# -> Fill rel_best_*.yaml using logged results in XX_REL_CARD.md 
```

### Evaluate (generate report)
```shell
# Generate CARD with best configs
for FORMAT in $(cat lib/formats.txt); 
do patentcity eval relationship-model data/gold_rel_${FORMAT}.jsonl configs/rel_best_${FORMAT}.yaml >> doc/XX_REL_CARD.md; 
done;
```

