This README documents the construction of "common\_borders.csv" since
1870. This document reports the gdp per capita, imports, exports, common
borders of 16 countries: Switzerland; Japan; Netherlands; Canada;
Sweden; Italy; Austria; Belgium; Russia; Australia; Czech Republic;
Denmark; Hungary; Poland; United States of America; Germany; France and
United Kingdom.

Notes:

-   Other data come from [Mayer, T. & Zignago, S. (2011) Notes on
    > CEPII's distances measures : the GeoDist Database *CEPII Working
    > Paper
    > 2011-25*](http://www.cepii.fr/CEPII/en/publications/wp/abstract.asp?NoDoc=3877)

Language, border, distance

+---------+-----------------------------------------------------------+
| Isocode | France isocode is "FRA" and not "FRN"                     |
+=========+===========================================================+
| R code  | llibrary(readr)                                           |
|         |                                                           |
|         | df3 \<- read\_csv(\"Perso/Stage/Stage 2021 CDF/Gravity    |
|         | analysis/Common borders/dist\_cepii.csv\")                |
|         |                                                           |
|         | df4=df3\[df3\$iso\_o==\"CHE\"                             |
|         | \|df3\$iso\_o==\"JPN\"\|df3\$iso\_o==\"NLD\"\|df3\$iso\_o |
|         | ==\"CAN\"\|df3\$iso\_o==\"SWE\"\|df3\$iso\_o==\"ITA\"\|df |
|         | 3\$iso\_o==\"AUT\"\|df3\$iso\_o==\"BEL\"\|df3\$iso\_o==\" |
|         | RUS\"\|df3\$iso\_o==\"AUS\"\|df3\$iso\_o==\"CZE\"\|df3\$i |
|         | so\_o==\"CSK\"\|df3\$iso\_o==\"DNK\"\|df3\$iso\_o==\"HUN\ |
|         | "\|df3\$iso\_o==\"POL\"\|df3\$iso\_o==\"USA\"\|df3\$iso\_ |
|         | o==\"GER\"\|df3\$iso\_o==\"FRA\"\|df3\$iso\_o==\"GBR\",\] |
|         |                                                           |
|         | df5=df4\[df4\$iso\_d==\"CHE\"                             |
|         | \|df4\$iso\_d==\"JPN\"\|df4\$iso\_d==\"NLD\"\|df4\$iso\_d |
|         | ==\"CAN\"\|df4\$iso\_d==\"SWE\"\|df4\$iso\_d==\"ITA\"\|df |
|         | 4\$iso\_d==\"AUT\"\|df4\$iso\_d==\"BEL\"\|df4\$iso\_d==\" |
|         | RUS\"\|df4\$iso\_d==\"AUS\"\|df4\$iso\_d==\"CZE\"\|df4\$i |
|         | so\_d==\"CSK\"\|df4\$iso\_d==\"DNK\"\|df4\$iso\_d==\"HUN\ |
|         | "\|df4\$iso\_d==\"POL\"\|df4\$iso\_d==\"USA\"\|df4\$iso\_ |
|         | d==\"GER\"\|df4\$iso\_d==\"FRA\"\|df4\$iso\_d==\"GBR\",\] |
|         |                                                           |
|         | df6=df5\[,c(1,2,3,4,11)\]                                 |
|         |                                                           |
|         | write.csv(df6, file=\"language\_border\_distance.csv\")   |
+---------+-----------------------------------------------------------+
