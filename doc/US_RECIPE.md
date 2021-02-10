# :cookie: Recipe

#### Serialize data

```shell
LANG=en
OFFICE=us
FORMAT=uspatent01 # uspatent02 uspatent03 uspatent04
patentcity brew v1 "data_${OFFICE}/${FORMAT}/*.txt" models/${LANG}_ent_${FORMAT}/model-best configs/config_rel_best_${FORMAT}.yaml >> entrel_${FORMAT}.jsonl
```

#### Prepare data for geocoding

#### HERE geocoding

#### Gmaps geocoding

#### Manual correction

#### Harmonize, combine and incorporate geocoded data

#### Build
