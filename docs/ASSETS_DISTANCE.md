# Distance

This document refers to [distance_xx.csv](https://github.com/cverluise/patentcity/tree/feature/assets/assets) which reports the pairwise distance between countries.

!!! info "Coverage"
    Australia (AUS), Austria (AUT), Belgium (BEL), Canada (CAN), Czech Republic (CZE), Denmark (DNK), France (FRA), Germany (DEU), Great Britain (GBR), Hungary (HUN), Italy (ITA), Japan (JPN), Netherlands (NLD), Poland (POL), Russia (RUS), Sweden (SWE), Switzerland (CHE), United States of America (USA)

## Metadata

Source: [Mayer, T. & Zignago, S. "Notes on CEPII's distances measures: the GeoDist Database". *CEPII Working  Paper 2011-25*. 2011](http://www.cepii.fr/CEPII/en/publications/wp/abstract.asp?NoDoc=3877)

## Variables

Variable|Description    | Type
---|---|---
origin_country_code     | Country code of the origin country| `str`
destination_country_code| Country code of the destination country | `str`
distance                | Distance between origin country and destination country (in [XX: add unit]) | `float`
