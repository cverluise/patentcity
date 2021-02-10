# :cookie: Recipe

#### Serialize data

````shell script
LANG=de
OFFICE=de
FORMAT=depatent01 # depatent02
patentcity brew v1 "data_${OFFICE}/${FORMAT}/*.txt" models/${LANG}_ent_${FORMAT}/model-best configs/config_rel_best_${FORMAT}.yaml >> entrel_${FORMAT}.jsonl
````
