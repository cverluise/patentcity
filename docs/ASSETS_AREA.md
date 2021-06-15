# AREA

File|Source
---|---
[area_xx.csv](https://github.com/cverluise/patentcity/tree/master/assets)  | DE [Rosés-Wolf database on regional GDP (version 6, 2020)](https://www.wiwi.hu-berlin.de/de/professuren/vwl/wg/roses-wolf-database-on-regional-gdp), FR [Wikipedia](https://fr.wikipedia.org/wiki/Liste_des_d%C3%A9partements_fran%C3%A7ais_class%C3%A9s_par_population_et_superficie), GB  [Wikipedia](https://simple.wikipedia.org/wiki/List_of_counties_of_the_United_Kingdom), US [Fabian Eckert, Andrés Gvirtz, Jack Liang, and Michael Peters. "A Method to Construct Geographical Crosswalks with an Application to US Counties since 1790." NBER Working Paper #26770, 2020](http://fpeckert.me/eglp/)

## Coverage

Country |Geographical level | Time
---|---|---
DE  |2 (nuts2)   | 2020
FR  |3 (nuts3)   | 2020
GB  |2 (nuts2)   | 2020
US  |2 (commuting zone)   | 2020

## Variables

Variable|Description    | Type
---|---|---
country_code            | Country code | `str`
statisticalAreaCode     | Statistical area code (nuts/fips) | `str`
statisticalAreaName     | Statistical area name (literal)| `str`
area                    | Area of the statistical area (in kilometers| `float`

??? note  "Focus on GB statistical areas construction"

    Some modern counties are made of a couple of older ones. In this case, we recompose modern counties or use the old name.

    statisticalAreaName | Construction
    ---|---
    City and County of the City of London | County of London (includes the city)
    Ross and Cromarty       | Ross-shire
    Roxburgh, Ettrick and Lauderdale | Roxburghshire + Selkirkshire + Berwickshire/4 + Midlothian/4
    Ayrshire and Arran      | South Ayrshire + North Ayrshire + East Ayrshire
    Tweeddale               | Peeblesshire
    Stirling and Falkirk    | Stirling + Falkirk
