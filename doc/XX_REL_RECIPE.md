# :cookie: Recipe


```shell
# generate configs
patentcity search relationship-params configs/config_rel_search.yaml

# Grid search for all formats
for FORMAT in $(ls data/gold_rel_*.jsonl | cut -d_ -f3 | cut -d. -f1); 
do ls configs/config_rel_*.yaml | grep -v search | grep -v best | parallel --eta "patentcity eval relationship-model data/gold_rel_${FORMAT}.jsonl {} --report json>> {.}_${FORMAT}.json" && echo "\n## ${FORMAT}" >> doc/XX_REL_CARD.md  && patentcity search relationship-best "configs/config_rel_*_${FORMAT}.json" >> doc/XX_REL_CARD.md; 
done; 


```