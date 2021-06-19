# Population

File | Source(s)
---|---
[population_xx.csv](https://github.com/cverluise/patentcity/tree/master/assets)  |DE [Rosés-Wolf database on regional GDP (version 6, 2020)](https://www.wiwi.hu-berlin.de/de/professuren/vwl/wg/roses-wolf-database-on-regional-gdp), FR [INSEE](https://www.insee.fr/fr/statistiques/3698339), GB [Vision of Britain](https://www.visionofbritain.org.uk/)&[Isle of man](http://www.isle-of-man.com/manxnotebook/history/pop.htm), US [Fabian Eckert, Andrés Gvirtz, Jack Liang, and Michael Peters. "A Method to Construct Geographical Crosswalks with an Application to US Counties since 1790." NBER Working Paper #26770, 2020](https://mipeters.weebly.com/uploads/1/4/6/5/14651240/egp_crosswalk.zip)

## Coverage

Country |Geographical level |Period
---|---|---
DE  |2 (nuts2)       | 1900-2015
FR  |3 (nuts3)       | 1876-2018
GB  |2 (nuts2)       | 1851-2011
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
