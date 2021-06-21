# Population

File | Source(s)
---|---
[population_xx.csv](https://github.com/cverluise/patentcity/tree/master/assets)  |DE [Rosés-Wolf database on regional GDP (version 6, 2020)](https://www.wiwi.hu-berlin.de/de/professuren/vwl/wg/roses-wolf-database-on-regional-gdp), FR [INSEE](https://www.insee.fr/fr/statistiques/3698339), GB [Vision of Britain](https://www.visionofbritain.org.uk/)&[ONS](https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/adhocs/13221populationestimatesbylocalauthoritiesofgreatbritainmid1981tomid2019)&[Wiki](https://en.wikipedia.org/wiki/Demography_of_Northern_Ireland), US [Fabian Eckert, Andrés Gvirtz, Jack Liang, and Michael Peters. "A Method to Construct Geographical Crosswalks with an Application to US Counties since 1790." NBER Working Paper #26770, 2020](https://mipeters.weebly.com/uploads/1/4/6/5/14651240/egp_crosswalk.zip)

## Coverage

Country |Geographical level |Period
---|---|---
DE  |2 (nuts2)       | 1900-2015
FR  |3 (nuts3)       | 1876-2018
GB  |2 (nuts2)       | 1851-2019
US  |2 (commuting zone) | 1830-2000

## Variables

Variable|Description    | Type
---|---|---
country_code            | Country code | `str`
statisticalAreaCode     | Statistical area code (nuts/fips) | `str`
statisticalAreaName     | Statistical area name (literal)| `str`
year                    | Year | `int`
population              | Population in the statistical area (in thousands)| `float`


??? note  "Focus on GB statistical areas construction"

    Some modern counties are made of a couple of older ones. In this case, we recompose modern counties or use the old name.

    statisticalAreaName | Construction
    ---|---
    Outer London — West and North West | Barnet + Brent + Ealing + Harrow + Hillingdon + Hounslow + Richmond upon Thames
    Outer London — South       | Bromley + Croydon + Merton + Kingston upon Thames + Sutton
    Outer London — East and North East | Bexley + Greenwich + Barking and Dagenham + Havering + Redbridge + Waltham Forest + Enfield
    Inner London — East      | Hackney + Newham + Tower Hamlets + Haringey + Islington + Lewisham + Southwark + Lambeth
    Inner London — West               | Camden + City of London + Westminster +Kensington & Chelsea + Hammersmith & Fulham + Wandsworth
    Tweeddale    | Peebles+Selkirkshire
    Roxburgh Ettrick and Lauderdale    | Roxburghshire + Selkirkshire + Berwickshire/4 + Midlothian/4
    Cheshire    | Halton + Warrington + Cheshire east + Cheshire West and Chester
    Mid Glamorgan    | Caerphilly/2 + Bridgend + Merthyr Tydfil + Rhondda; Cynon; Taff
    South Glamorgan    | Vale of Glamorgan + Cardiff
    Clwyd    | Flintshire + Wrexham + Denbighshire
    Dyfed    | Carmarthenshire + Ceredigion + Pembrokeshire
    Gwent    | Blaenau Gwent + Caerphilly/2 + Monmouthshire + Newport + Torfaen
    Vale of Glamorgan    | Glamorganshire
    
    Then, with the "Conversion_VoB_NUTS_GB.csv" document we convert VoB data into NUTS 2 level data. To do so, we complete the VOB dataset with linear interpolation because one missing data prevent us from reconstituting the whole NUTS 2 entity in 1871, 1901 and 1941 (e.g. Bedfordshire in 1941).
    For Wales and Scotland data are missing since 1981. We suppose population increased homogeneously in each NUTS so we determine 1981 NUTS population by multiplying 1971 NUTS population by the population growth rate in those countries from 1971 to 1981.
    NUTS 3 data are available for each year since 1981, we convert them into NUTS 2 data thanks to an online conversion table (e.g https://en.wikipedia.org/wiki/NUTS_statistical_regions_of_the_United_Kingdom).
    As pre-1981 data are constructed with  VOB data and not NUTS 3 data, we correct potential errors by retropolating the data, based on a comparison between our NUTS 2 "artificial" data (constructed with VOB) in 1981 and "official" NUTS 2 data (constructed with NUTS 3) in 1981.
