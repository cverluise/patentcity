# MODELS

## Train and Evaluate

```shell
# generate configs
patentcity search relationship-params configs/rel_search.yaml

# Grid search for all formats
for FORMAT in $(cat lib/formats.txt);
do ls configs/rel_*.yaml | grep -v search | grep -v best | parallel --eta "patentcity eval relationship-model data/gold_rel_${FORMAT}.jsonl {} --report json>> {.}_${FORMAT}.json" && echo "\n## ${FORMAT}" >> doc/XX_REL_CARD.md  && patentcity search relationship-best "configs/rel_*_${FORMAT}.json" >> doc/XX_REL_CARD.md;
done;
# -> Fill rel_best_*.yaml using logged results in XX_REL_CARD.md

# Generate CARD with best configs
for FORMAT in $(cat lib/formats.txt);
  do patentcity eval relationship-model data/gold_rel_${FORMAT}.jsonl configs/rel_best_${FORMAT}.yaml >> doc/XX_REL_CARD.md;
done;
```

## ddpatent01
|    |   ALL |   LOCATION | CITIZENSHIP   |   OCCUPATION |
|:---|------:|-----------:|:--------------|-------------:|
| p  | 0.99  |      0.99  |               |        0.992 |
| r  | 0.979 |      0.992 |               |        0.936 |
| f  | 0.985 |      0.991 |               |        0.964 |

## ddpatent02
|    |   ALL |   LOCATION | CITIZENSHIP   |   OCCUPATION |
|:---|------:|-----------:|:--------------|-------------:|
| p  | 0.907 |      0.981 |               |        0.767 |
| r  | 0.89  |      0.933 |               |        0.803 |
| f  | 0.899 |      0.956 |               |        0.785 |


## depatent01
|    |   ALL |   LOCATION | CITIZENSHIP   | OCCUPATION   |
|:---|------:|-----------:|:--------------|:-------------|
| p  | 0.967 |      0.991 |               |              |
| r  | 0.875 |      0.997 |               |              |
| f  | 0.918 |      0.994 |               |              |


## depatent02
|    |   ALL |   LOCATION | CITIZENSHIP   |   OCCUPATION |
|:---|------:|-----------:|:--------------|-------------:|
| p  | 0.994 |      0.996 |               |        0.985 |
| r  | 0.988 |      0.987 |               |        0.992 |
| f  | 0.991 |      0.991 |               |        0.988 |


## frpatent01
|    |   ALL |   LOCATION | CITIZENSHIP   | OCCUPATION   |
|:---|------:|-----------:|:--------------|:-------------|
| p  | 0.99  |      0.99  |               |              |
| r  | 0.962 |      0.962 |               |              |
| f  | 0.976 |      0.976 |               |              |

## frpatent02
|    |   ALL |   LOCATION | CITIZENSHIP   | OCCUPATION   |
|:---|------:|-----------:|:--------------|:-------------|
| p  | 0.984 |      0.984 |               |              |
| r  | 0.997 |      0.997 |               |              |
| f  | 0.991 |      0.991 |               |              |

## gbpatent01
|    |   ALL |   LOCATION |   CITIZENSHIP |   OCCUPATION |
|:---|------:|-----------:|--------------:|-------------:|
| p  | 0.954 |      0.974 |         0.924 |        0.961 |
| r  | 0.93  |      0.926 |         0.931 |        0.943 |
| f  | 0.942 |      0.949 |         0.928 |        0.952 |

## uspatent01
|    |   ALL |   LOCATION |   CITIZENSHIP | OCCUPATION   |
|:---|------:|-----------:|--------------:|:-------------|
| p  | 0.983 |      0.983 |         0.981 |              |
| r  | 0.972 |      0.97  |         0.978 |              |
| f  | 0.977 |      0.977 |         0.98  |              |


## uspatent02
|    |   ALL |   LOCATION |   CITIZENSHIP | OCCUPATION   |
|:---|------:|-----------:|--------------:|:-------------|
| p  | 0.978 |      0.977 |         0.983 |              |
| r  | 0.986 |      0.989 |         0.975 |              |
| f  | 0.982 |      0.983 |         0.979 |              |

## uspatent03
|    |   ALL |   LOCATION |   CITIZENSHIP | OCCUPATION   |
|:---|------:|-----------:|--------------:|:-------------|
| p  | 0.987 |      0.993 |         0.97  |              |
| r  | 0.994 |      0.998 |         0.982 |              |
| f  | 0.991 |      0.995 |         0.976 |              |

## uspatent04
|    |   ALL |   LOCATION |   CITIZENSHIP | OCCUPATION   |
|:---|------:|-----------:|--------------:|:-------------|
| p  | 0.98  |       0.98 |               |              |
| r  | 0.815 |      0.815 |               |              |
| f  | 0.89  |       0.89 |               |              |
