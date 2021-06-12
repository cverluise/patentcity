This README documents the construction of population\_de.csv from 1871
to 2003. This document reports the population of each german Lander
listed on
<https://en.wikipedia.org/wiki/NUTS_statistical_regions_of_Germany> .

Notes:

\- Unless specified, the data source is tacitus.nu
([[https://www.tacitus.nu/historical-atlas/population/germany.htm]{.underline}](https://www.tacitus.nu/historical-atlas/population/germany.htm))

\- Counties changed over the period of interest. We use Modern German
Lander.

Focus on moving boundaries and multi data-source counties
---------------------------------------------------------

Some modern Landers are made of a couple of older ones. In this case, we
recompose modern Landers based on the data available for the existing
Landers at the time of the census. We use wikipedia historical Lander
descriptions to know which state should be aggregated. We sometimes
approximate modern frontiers by comparing 1939 modern state inhabitant
data to 1939 Reich state or Prussian boundaries. For 2 different 1910
data, I keep interwar data

+----------------+----------------+----------------+----------------+
| Lander         | Source         | Construction   |                |
+================+================+================+================+
| Berlin         |                | 1939-2010:     | In 1920 Berlin |
|                |                | East Berlin +  | became Great   |
|                |                | West Berlin    | Berlin         |
|                |                |                |                |
|                |                | 1870-1900:     | Part of        |
|                |                | Berlin+0.4     | Brandenburg    |
|                |                | 4\*Brandenburg | became Berlin: |
|                |                |                |                |
|                |                |                | 2 % of the     |
|                |                |                | surface        |
|                |                |                |                |
|                |                |                | 44 % of the    |
|                |                |                | population     |
+----------------+----------------+----------------+----------------+
| Mecklenb       | http           | 1870-1939:     |                |
| urg-Vorpommern | s://de.wikiped | Mecklenburg+0  |                |
|                | ia.org/wiki/Pr | ,3\*Vorpommern |                |
|                | ovinz\_Pommern |                |                |
+----------------+----------------+----------------+----------------+
| Hessen         |                | 1870-1939:     |                |
|                |                | Using          |                |
|                |                | Hessen-Nassau  |                |
|                |                | (prussian      |                |
|                |                | boundaries     |                |
|                |                | instead of     |                |
|                |                | Reich)         |                |
+----------------+----------------+----------------+----------------+
| Saarland       | <http          | 1870-1939:     |                |
|                | s://doi.org/10 | Daric(1955)    |                |
|                | .2307/1524412> |                |                |
+----------------+----------------+----------------+----------------+
| Bad            |                | 1870-1939:     |                |
| en-Württemberg |                | Bad            |                |
|                |                | en+Württemberg |                |
+----------------+----------------+----------------+----------------+
| Rheinland-Palz |                | 1870-1939:     |                |
|                |                | 0.4\*Rheinland |                |
+----------------+----------------+----------------+----------------+
| Nordr          |                | 1870-1939:     |                |
| hein-Westfalen |                | 2,3\*Westfalen |                |
|                |                | (as            |                |
|                |                | N              |                |
|                |                | ordrhein-Westf |                |
|                |                | alen/Westfalen |                |
|                |                | = 2,3 in 1939) |                |
+----------------+----------------+----------------+----------------+
| Saxony         |                | Reich borders  |                |
|                |                | as data are    |                |
|                |                | closer to      |                |
|                |                | "modern state  |                |
|                |                | border"        |                |
+----------------+----------------+----------------+----------------+
