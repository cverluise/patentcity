# Population

File | Source(s)
---|---
[population_xx.csv](https://github.com/cverluise/patentcity/tree/master/assets) |DE: [Rosés-Wolf database on regional GDP (version 6, 2020)](https://www.wiwi.hu-berlin.de/de/professuren/vwl/wg/roses-wolf-database-on-regional-gdp)(pre 1990) & [Eurostat](https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Population_statistics_at_regional_level)(post 1990), FR: [INSEE](https://www.insee.fr/fr/statistiques/3698339), GB: [Vision of Britain](https://www.visionofbritain.org.uk/) (pre 1981) & [ONS](https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/adhocs/13221populationestimatesbylocalauthoritiesofgreatbritainmid1981tomid2019) (post 1981) & [Wiki](https://en.wikipedia.org/wiki/Demography_of_Northern_Ireland) (Northern Ireland) and [Census](https://data.london.gov.uk/dataset/historic-census-population) (London), US: [Fabian Eckert, Andrés Gvirtz, Jack Liang, and Michael Peters. "A Method to Construct Geographical Crosswalks with an Application to US Counties since 1790." NBER Working Paper #26770, 2020](https://mipeters.weebly.com/uploads/1/4/6/5/14651240/egp_crosswalk.zip)(1830-1970) & [Census](https://www.census.gov/data/tables/time-series/demo/popest/2010s-counties-total.html)(1970-2010) & [NBER data](https://data.nber.org/data/census-intercensal-county-population.html)(2010-2018)

## Coverage

Country |Geographical level |Period
---|---|---
DE  |2 (nuts2)       | 1900-2017
FR  |3 (nuts3)       | 1876-2017
GB  |2 (nuts2)       | 1851-2017
US  |2 (county) | 1830-2018

??? note  "Annual data"

    We proceed to a linear interpolation based on _population_raw_ column to obtain population data for each year in _population_ column.

## Variables

Variable|Description    | Type
---|---|---
country_code            | Country code | `str`
statisticalAreaCode     | Statistical area code (nuts/fips) | `str`
statisticalAreaName     | Statistical area name (literal)| `str`
year                    | Year | `int`
population              | Population in the statistical area (in thousands)| `float`
population\_raw         | Population in the statistical area before correction (in thousands). Relevant for GB only (see notes below)| `float`

??? note  "Focus on US data"

    We obtain US population post 1970 data by aggregating county data thanks to [David Dorn crossover table](https://www.ddorn.net/data.htm).

??? note  "Focus on GB data"

    GB population data are not available at a sufficiently detailed NUTS level over long period - at least we did not find it. For instance, Rosés and Wolf (2020) only provides data at the NUTS1 level for GB. Hence, we had to build the population data for GB at the NUTS2 level ourselves. This includes 3 main stages: 1. Pre-1981 data collection, 2. Post-1981 data collection, 3. Data harmonization

    **Pre-1981 data collection**:

    We use Vision of Britain (VoB) population data, except for London where we use data from the Census. Some VoB geographic entities have no population data though. In this case, we made our best to reconstitute the data from smaller entities with known population data. Below we detail the construction of these entities

    VoB | Construction
    ---|---
    Tweeddale    | Peebles+Selkirkshire
    Roxburgh Ettrick and Lauderdale    | Roxburghshire + Selkirkshire + Berwickshire/4 + Midlothian/4
    Cheshire    | Halton + Warrington + Cheshire east + Cheshire West and Chester
    Mid Glamorgan    | Caerphilly/2 + Bridgend + Merthyr Tydfil + Rhondda; Cynon; Taff
    South Glamorgan    | Vale of Glamorgan + Cardiff
    Clwyd    | Flintshire + Wrexham + Denbighshire
    Dyfed    | Carmarthenshire + Ceredigion + Pembrokeshire
    Gwent    | Blaenau Gwent + Caerphilly/2 + Monmouthshire + Newport + Torfaen
    Vale of Glamorgan    | Glamorganshire

    Missing VoB data (concentrated in 1871, 1901 and 1941) are filled with linear interpolation.

    Once we have data for all VoB entities (real or imputed), we aggregate them to obtain population data at the NUTS2 level using the conversion table reported in [statisticalareasvob_gb.csv](https://github.com/cverluise/patentcity/tree/master/assets).

    **Post-1981 data collection**

    After 1981, the ONS  provides data at the local authority level for each year. Same as before, we aggregate them to obtain population data at the NUTS2 level using the conversion table reported in [statisticalareaslau_gb.csv](https://github.com/cverluise/patentcity/tree/master/assets). The conversion table is based on the [local authority to NUTS crossover table](https://data.gov.uk/dataset/86beb640-9fa4-4131-b330-fc26d74c074f/local-authority-district-december-2018-to-nuts3-to-nuts2-to-nuts1-january-2018-lookup-in-united-kingdom) and the [Scotish Review of NUTS boundaries](https://www.gov.scot/publications/review-nomenclature-units-territorial-statistics-nuts-boundaries/).

    **Data harmonization**

    As pre-1981 data are constructed using a collection of sources creating potential flaws or approximations. Hence, we found it desirable to compare the two datasets in 1981 (the only year of overlap) to compute a correction coefficient obtained as $\frac{population~in~1981~using~ONS~data_{NUTS2}}{population~in~1981~using~VoB~data_{NUTS2}}$. We then apply this correction coefficient to all pre-1981 data to make sure that the time series is consistent for each NUTS2 despite the data source change.

    Note that for East Wales and Scotland, 1981 (and 1971 for East Wales) data are missing from VoB. We used the 1971 data and applied the national population growth rate to (roughly) estimate the VoB data and hence the correction coefficient.
