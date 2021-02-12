# :cookie: Recipe


```shell
# generate configs
patentcity search relationship-params configs/rel_search.yaml

# Grid search for all formats
for FORMAT in $(ls data/gold_rel_*.jsonl | cut -d_ -f3 | cut -d. -f1); 
do ls configs/rel_*.yaml | grep -v search | grep -v best | parallel --eta "patentcity eval relationship-model data/gold_rel_${FORMAT}.jsonl {} --report json>> {.}_${FORMAT}.json" && echo "\n## ${FORMAT}" >> doc/XX_REL_CARD.md  && patentcity search relationship-best "configs/rel_*_${FORMAT}.json" >> doc/XX_REL_CARD.md; 
done; 
# -> Fill rel_best_*.yaml using logged results in XX_REL_CARD.md 

# Generate CARD with best configs
for FORMAT in $(ls data/gold_rel_*.jsonl_corr | cut -d_ -f 3 | cut -d. -f1); 
do patentcity eval relationship-model data/gold_rel_${FORMAT}.jsonl configs/rel_best_${FORMAT}.yaml >> doc/XX_REL_CARD.md; 
done;
```