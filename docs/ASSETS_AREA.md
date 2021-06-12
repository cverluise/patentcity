Read Me

This README documents the construction of area\_fr, area\_de, area\_us,
area\_gb. We determine the area of each geographical unit used for
population evolution.

Notes:

-US: Data source is the population file document.

-FR: Data source is:
[[https://fr.wikipedia.org/wiki/Liste\_des\_d%C3%A9partements\_fran%C3%A7ais\_class%C3%A9s\_par\_population\_et\_superficie]{.underline}](https://fr.wikipedia.org/wiki/Liste_des_d%C3%A9partements_fran%C3%A7ais_class%C3%A9s_par_population_et_superficie)

-UK: Data source is:
[[https://simple.wikipedia.org/wiki/List\_of\_counties\_of\_the\_United\_Kingdom]{.underline}](https://simple.wikipedia.org/wiki/List_of_counties_of_the_United_Kingdom)

As not all geographical units chosen for the population evolution part

-DE: Data source
is:[[https://en.wikipedia.org/wiki/List\_of\_German\_states\_by\_area]{.underline}](https://en.wikipedia.org/wiki/List_of_German_states_by_area)

Focus on UK additional data:
----------------------------

+----------------------+----------------------+----------------------+
|                      | Construction         |                      |
+======================+======================+======================+
| City and County of   | County of London     |                      |
| the City of London   | (includes the city)  |                      |
+----------------------+----------------------+----------------------+
| Ross and Cromarty    | Ross-shire           |                      |
+----------------------+----------------------+----------------------+
| Roxburgh, Ettrick    | Roxburghshire+       |                      |
| and Lauderdale       | Selkirkshire+Berwick |                      |
|                      | shire/4+Midlothian/4 |                      |
|                      |                      |                      |
|                      | (same construction   |                      |
|                      | as for population    |                      |
|                      | data)                |                      |
+----------------------+----------------------+----------------------+
| Ayrshire and Arran   | South\               | "Ayrshire and Arran  |
|                      | _Ayrshire+North\_Ayr | is a lieutenancy     |
|                      | shire+East\_Ayrshire | area of Scotland. It |
|                      |                      | consists of the      |
|                      |                      | council areas of     |
|                      |                      | East Ayrshire, North |
|                      |                      | Ayrshire and South   |
|                      |                      | Ayrshire."           |
+----------------------+----------------------+----------------------+
| Tweeddale            | Peeblesshire         | "Its boundaries      |
|                      |                      | correspond to the    |
|                      |                      | historic county of   |
|                      |                      | Peeblesshire"        |
+----------------------+----------------------+----------------------+
| Stirling and Falkirk | Stirling+Falkirk     |                      |
+----------------------+----------------------+----------------------+
