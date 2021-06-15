# Population

This document refers to [population_xx.csv](https://github.com/cverluise/patentcity/tree/master/assets) which reports the population by statistical areas.

## Metadata

File | Source(s)
---|---
[population_xx.csv](https://github.com/cverluise/patentcity/tree/master/assets)  |DE [Rosés-Wolf database on regional GDP (version 6, 2020)](https://www.wiwi.hu-berlin.de/de/professuren/vwl/wg/roses-wolf-database-on-regional-gdp), FR INSEE, GB [Vision of Britain](https://www.visionofbritain.org.uk/), US [Fabian Eckert, Andrés Gvirtz, Jack Liang, and Michael Peters. "A Method to Construct Geographical Crosswalks with an Application to US Counties since 1790." NBER Working Paper #26770, 2020](http://fpeckert.me/eglp/)

## Coverage

Country |Geographical level |Period
---|---|---
DE  |2(nuts2)       | 1900-2015
FR  |3(nuts3)       | 1876-2018
GB  |2(nuts2)       | 1851-2011
US  |2 (commuting zone) | 1830-2000

## Variables

Variable|Description    | Type
---|---|---
country_code            | Country code | `str`
statisticalAreaCode     | Statistical area code (nuts/fips) | `str`
statisticalAreaName     | Statistical area name (literal)| `str`
year                    | Year | `int`
population              | Population in the statistical area (in thousands)| `float`
