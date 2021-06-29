# SHAPEFILES


Files | Source(s)
---|---
[boundariesnust2_[de,fr,gb].shp.tar.gz](https://github.com/cverluise/patentcity/tree/master/assets) | [Eurostat](https://ec.europa.eu/eurostat/fr/web/gisco/geodata/reference-data/administrative-units-statistical-units/nuts)
[boundariescz1990_us.shp.tar.gz](https://github.com/cverluise/patentcity/tree/master/assets)|[Health inequality project](https://healthinequality.org/dl/cz1990_shapefile.zip)

## Coverage

Country |Geographical level |Year
---|---|---
DE  |2 (nuts2)       | 2021
FR  |2 (nuts2)       | 2021
GB  |2 (nuts2)       | 2021
US  |2 (commuting zone) | 1990

## Variables

Variable|Description    | Type
---|---|---
cntr_code| Country code | `str`
code     | Nuts2 code/commuting zone code | `str`
geometry | Shape| `geometry`

??? Snippet "Untar shapefile"
    ```shell
    tar -xvzf assets/boundariescz1990_us.shp.tar.gz
    ```
