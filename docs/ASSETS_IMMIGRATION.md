This README documents the construction of immigration\_us.csv from 1850
to 2000. This document reports share and the number of foreign-born in
the US and specifies their origins (data for 1950 and 1940 are missing).

Notes:

-   The data source is census.gov (e.g
    > [[https://www.census.gov/content/dam/Census/library/working-papers/2006/demo/POP-twps0081.pdf]{.underline}](https://www.census.gov/content/dam/Census/library/working-papers/2006/demo/POP-twps0081.pdf)
    > )

-   Some countries appeared or were intégrated in larger entities

-   Wales unitary authorities are an aggregation of districts made
    > thanks to wikipedia historical description of the county.

Focus on moving boundaries and multi data-source counties
---------------------------------------------------------

Some countries appeared or were integrated in larger entities, we
therefore specify if the data is missing or if there is only integrated
data.

The table from census.gov proposes different scales, we integer a new
column to specify the scale and we name each scale in this read me.

Our table should be read as each row is the sum of the rows with a
strictly lower "key" value (e.g Scandinavia is the sum of Denmark,
Finland, Iceland, Norway, Sweeden and Other Scandinavia).

+------------------------------+--------------------------------------+
| Missing data/ not applicable | Missing data are left blank          |
|                              |                                      |
|                              | Not applicable data "(X)"            |
+==============================+======================================+
| "Key" column specifications  | 9: Total                             |
|                              |                                      |
|                              | 8:Subtotals                          |
|                              |                                      |
|                              | 7: Continent                         |
|                              |                                      |
|                              | 6: Continental areas                 |
|                              |                                      |
|                              | 5: European regions                  |
|                              |                                      |
|                              | 4: Other regions                     |
|                              |                                      |
|                              | 3:United Kingdom                     |
|                              |                                      |
|                              | 2: Country groups                    |
|                              |                                      |
|                              | 1: Countries                         |
|                              |                                      |
|                              | (For the moment we note "Europe      |
|                              | n.e.c", "Soviet Union (former) and   |
|                              | "In Europe" as key 1)                |
+------------------------------+--------------------------------------+

Glossary:

Low countries = BelgiumLuxembourgNetherlands

n.e.c. Not elsewhere classified
