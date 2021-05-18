# STATISTICAL AREAS

## Problem

We harvest administrative areas from the geocoding. They are already useful, but they have some limitations:

- spelling inconsistencies between geocoding services (e.g. "Constance" vs "Konstanz")
- semantic inconsistencies between geocoding services (e.g. districts vs kreis as level 3 adminstritative area for DE)

In addition, we would like to have the following features:

- overall comparability of areas between countries. We would like to be able to compare countries based on comparable objects (e.g. [NUTS](https://en.wikipedia.org/wiki/Nomenclature_of_Territorial_Units_for_Statistics))
- common statistical usage. We want to be able to interact our data with external statistics (e.g. demographic data, economic data, structural data)

## Approach

The first group of issues (spelling and semantic inconsistencies) is solved using hand-made dictionaries. Fully documented by issue [#7](https://github.com/cverluise/patentcity/issues/7).

For the second group of issues, we define two levels of "statistical areas" (level 1 being more aggregated than level 2).

Country code| Statistical area 1| Statitical area 2
----|----|----
DD  |-   |-
DE  |NUTS1 (Land)   |NUTS2 (District)
FR  |NUTS1 (Région) |NUTS3 (Département)
GB  |NUTS1          |Ceremonial counties for England, Lieutenancy Areas for Scotland, Preserved counties for Wales and Northern Ireland (as a whole)
US  |State          |Commuting Zone (1990)

!!! info
    - [NUTS Europe (2021)](https://ec.europa.eu/eurostat/documents/345175/629341/NUTS2021.xlsx)
    - [Postal code to NUTS Europe (2021)](https://gisco-services.ec.europa.eu/tercet/flat-files)
    - [County to Commuting zone (1990)](http://fpeckert.me/eglp/)

Except for the US, we can use the postal code as the primary key for statistical areas.

??? quote "Postal code as a primary key?"

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
