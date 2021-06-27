# GDP share agriculture

File |Source
---|---
[gdpshareagriculture_xx.csv](https://github.com/cverluise/patentcity/tree/master/assets)| [Rosés-Wolf database on regional GDP (version 6, 2020)](https://www.wiwi.hu-berlin.de/de/professuren/vwl/wg/roses-wolf-database-on-regional-gdp)

## Coverage

Country |Geographical level | Period
---|---|---
DE  |2 (nuts2)       | 1900-2015
FR  |2 (nuts2)       | 1900-2015
GB  |1 (nuts1)       | 1900-2015

!!! warning
    US not supported yet

## Variables

Variable|Description    | Type
---|---|---
country_code        | Country code  | `str`
statisticalAreaCode | Statistical area code  | `str`
statisticalArea     | Statistical area  | `str`
year                | Year  | `int`
share_agriculture                 | Share of GDP represented by the agriculture sector (in %) | `float`
