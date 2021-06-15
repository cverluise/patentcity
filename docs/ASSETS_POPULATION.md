# Population

This document refers to [population_xx.csv](https://github.com/cverluise/patentcity/tree/master/assets) which reports the population by statistical areas.

## Metadata

Country |Geographical level |Source(s)
---|---|---
DE  |2(nuts2)       | [Rosés-Wolf database on regional GDP (version 6, 2020)](https://www.wiwi.hu-berlin.de/de/professuren/vwl/wg/roses-wolf-database-on-regional-gdp)
FR  |3(nuts3)       | INSEE
GB  |2(nuts2)       | [Vision of Britain](https://www.visionofbritain.org.uk/)
US  |2 (commuting zone) | [Fabian Eckert, Andrés Gvirtz, Jack Liang, and Michael Peters. "A Method to Construct Geographical Crosswalks with an Application to US Counties since 1790." NBER Working Paper #26770, 2020](http://fpeckert.me/eglp/)

## Variables

Variable|Description    | Type
---|---|---
country_code            | Country code | `str`
statisticalAreaCode     | Statistical area code (nuts/fips) | `str`
statisticalAreaName     | Statistical area name (literal)| `str`
year                    | Year | `int`
population              | Population in the statistical area (in thousands)| `float`
