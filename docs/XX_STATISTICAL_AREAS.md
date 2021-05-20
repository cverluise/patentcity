# STATISTICAL AREAS

## Problem

We harvest administrative areas from the geocoding. They are already useful, but they have some limitations. In particular, they are not fully satisgying regarding the following features:

- between country comparability. We would like to be able to compare countries based on comparable objects (e.g. [NUTS](https://en.wikipedia.org/wiki/Nomenclature_of_Territorial_Units_for_Statistics))
- common usage. We want to be able to interoperate our data with external statistics (e.g. demographic data, economic data, structural data)

## Approach

We define three levels of "statistical areas". Level 1 is more aggregated than level 2 and so on. The below table details the statistical areas for each country.

Country code| Statistical area 1| Statistical area 2| Statistical area 3
----|----|----|----
DD  |-   |-   |-
DE  |NUTS1    |NUTS2    |NUTS3
FR  |NUTS1    |NUTS2    |NUTS3
GB  |NUTS1    |NUTS2    |NUTS3
US  |State    |Commuting Zone (1990) | County

!!! info
    - [NUTS Europe (2021)](https://ec.europa.eu/eurostat/documents/345175/629341/NUTS2021.xlsx)
    - [Postal code to NUTS Europe (2021)](https://gisco-services.ec.europa.eu/tercet/flat-files)
    - [County to Commuting zone (1990)](http://fpeckert.me/eglp/)



??? quote "Mapping key?"

    Except for the US, we can use the postal code as the primary key for statistical areas. For the US, we us the combination of the state and county (or state and city if county is null).

    ```sql
    WITH tmp AS (
    SELECT
      country_code,
      CAST(patentee.loc_state IS NOT NULL AS INT64) AS has_state,
      CAST(patentee.loc_county IS NOT NULL AS INT64) AS has_county,
      CAST(patentee.loc_postalCode IS NOT NULL AS INT64) AS has_postalCode,
    FROM
      `patentcity.patentcity.v100rc3`,
      UNNEST(patentee) AS patentee
    #WHERE
    #  publication_date<=19800000
    )
    SELECT
      country_code,
      SUM(has_state) as has_state,
      SUM(has_county) as has_county,
      SUM(has_postalCode) as has_postalCode
    FROM
      tmp
    GROUP BY
      country_code
    ```

    country\_code| has\_state| has\_county| has\_postalCode
    ----|----       |----       |----
    DD  |495479     |495479     |495479
    DE  |7284246    |6555370    |7366705
    FR  |1881112    |1872960    |1864284
    GB  |1759783    |1709290    |1750767
    US  |39675118   |29133272   |12382827


## Related issue


Administrative areas obtained directly from the geocoding services (`loc_state` and `loc_counties`) also exhibit intrinsic limitations:

- spelling inconsistencies between geocoding services (e.g. "Constance" vs "Konstanz")
- semantic inconsistencies between geocoding services (e.g. districts vs kreis as level 3 adminstritative area for DE)

Although we recommend the use of statistical areas, we also propose a solution using hand-made crossover tables. We do not implement the harmonization directly in the database as this is partly destructive. The solution (and its history) is described by issue [#7](https://github.com/cverluise/patentcity/issues/7).
