# AREA

## Metadata

File|Source
---|---
[area_xx.csv](https://github.com/cverluise/patentcity/tree/master/assets) |DE [Wikipedia](https://en.wikipedia.org/wiki/List_of_German_states_by_area), FR [Wikipedia](https://fr.wikipedia.org/wiki/Liste_des_d%C3%A9partements_fran%C3%A7ais_class%C3%A9s_par_population_et_superficie), GB [Wikipedia](https://simple.wikipedia.org/wiki/List_of_counties_of_the_United_Kingdom), US  [XX]

## Coverage

Country |Geographical level | Time
---|---|---
DE  |[XX]   | [XX]
FR  |[XX]   | [XX]
GB  |[XX]   | [XX]
US  |[XX]   | [XX]

## Variables

Variable|Description    | Type
---|---|---
country_code            | Country code | `str`
statisticalAreaCode     | Statistical area code (nuts/fips) | `str`
statisticalAreaName     | Statistical area name (literal)| `str`
area                    | Area of the statistical area (in [XX: add unit])| `float`

??? note  "Focus on GB statistical areas construction"

    [XX: add short note explaining why we need a specific treatment here]

    statisticalAreaName | Construction
    ---|---
    City and County of the City of London | County of London (includes the city)
    Ross and Cromarty       | Ross-shire
    Roxburgh, Ettrick and Lauderdale | Roxburghshire + Selkirkshire + Berwickshire/4 + Midlothian/4
    Ayrshire and Arran      | South Ayrshire + North Ayrshire + East Ayrshire
    Tweeddale               | Peeblesshire
    Stirling and Falkirk    | Stirling + Falkirk
