This README documents the construction of population\_gb.csv from 1851
to 2011. This document reports the population of each GB county.

Notes:

-   Unless specified, the data source is visionofbritain.org.uk (e.g
    > [[https://www.visionofbritain.org.uk/unit/10032921/cube/TOT\_POP]{.underline}](https://www.visionofbritain.org.uk/unit/10032921/cube/TOT_POP))

-   Counties changed over the period of interest. We use modern counties
    > and districts/Unitary Authorities.

-   Wales unitary authorities are an aggregation of districts made
    > thanks to wikipedia historical description of the county.

Focus on moving boundaries and multi data-source counties
---------------------------------------------------------

Some modern counties are made of a couple of older ones. In this case,
we recompose modern counties based on the data available for the
existing counties at the time of the census. We use wikipedia historical
county descriptions to know which counties should be aggregated.

+----------------+----------------+----------------+----------------+
| County         | Particularity  | Source         | Construction   |
+================+================+================+================+
| Berkshire      | I use          | From 1851 to   | "Boundary      |
|                | wikipedia data | 2011           | alterations in |
|                | over VoB data  |                | the early part |
|                | as the         | [[htt          | of the 20th    |
|                | difference     | ps://en.wikipe | century were   |
|                | between both   | dia.org/wiki/C | minor, with    |
|                | data is small  | heshire\#Popul | Caversham from |
|                | and wiki data  | ation]{.underl | Oxfordshire    |
|                | is more        | ine}](https:// | becoming part  |
|                | complete       | en.wikipedia.o | of the Reading |
|                |                | rg/wiki/Cheshi | county borough |
|                | (voB:[[        | re#Population) | and cessions   |
|                | https://www.vi |                | in the Oxford  |
|                | sionofbritain. |                | area."         |
|                | org.uk/unit/10 |                |                |
|                | 025084/cube/TO |                | Wikipedia      |
|                | T\_POP]{.under |                |                |
|                | line}](https:/ |                |                |
|                | /www.visionofb |                |                |
|                | ritain.org.uk/ |                |                |
|                | unit/10025084/ |                |                |
|                | cube/TOT_POP)) |                |                |
+----------------+----------------+----------------+----------------+
| Greater London | Three sources  | [              |                |
|                | are usable,    | [https://www.v |                |
|                | data from both | isionofbritain |                |
|                | websites are   | .org.uk/unit/1 |                |
|                | really close   | 0097836/cube/T |                |
|                | but            | OT\_POP]{.unde |                |
|                | data.b         | rline}](https: |                |
|                | ritain.gouv.uk | //www.visionof |                |
|                | is more        | britain.org.uk |                |
|                | complete I     | /unit/10097836 |                |
|                | therefore      | /cube/TOT_POP) |                |
|                | chose those    |                |                |
|                | data.          | [[             |                |
|                |                | http://www.dem |                |
|                |                | ographia.com/d |                |
|                |                | m-lonarea.htm] |                |
|                |                | {.underline}]( |                |
|                |                | http://www.dem |                |
|                |                | ographia.com/d |                |
|                |                | m-lonarea.htm) |                |
+----------------+----------------+----------------+----------------+
| County of      |                | [              | "The **County  |
| London         |                | [https://www.v | of London**    |
|                |                | isionofbritain | was a county   |
|                |                | .org.uk/unit/1 | of             |
|                |                | 0076845/cube/T | [Engla         |
|                |                | OT\_POP]{.unde | nd](https://en |
|                |                | rline}](https: | .wikipedia.org |
|                |                | //www.visionof | /wiki/England) |
|                |                | britain.org.uk | from 1889 to   |
|                |                | /unit/10076845 | 1965,          |
|                |                | /cube/TOT_POP) | corresponding  |
|                |                |                | to the area    |
|                |                |                | known today as |
|                |                |                | [Inner         |
|                |                |                | London](htt    |
|                |                |                | ps://en.wikipe |
|                |                |                | dia.org/wiki/I |
|                |                |                | nner_London)." |
|                |                |                |                |
|                |                |                | Wikipedia      |
+----------------+----------------+----------------+----------------+
| Ro             |                | https://e      | "It            |
| xburgh,Ettrick |                | n.wikipedia.or | corresponds    |
| and Lauderdale |                | g/wiki/Roxburg | broadly to the |
|                |                | h,\_Ettrick\_a | [count         |
|                |                | nd\_Lauderdale | ies](https://e |
|                |                |                | n.wikipedia.or |
|                |                |                | g/wiki/Countie |
|                |                |                | s_of_Scotland) |
|                |                |                | of             |
|                |                |                | [Rox           |
|                |                |                | burghshire](ht |
|                |                |                | tps://en.wikip |
|                |                |                | edia.org/wiki/ |
|                |                |                | Roxburghshire) |
|                |                |                | and            |
|                |                |                | [S             |
|                |                |                | elkirkshire](h |
|                |                |                | ttps://en.wiki |
|                |                |                | pedia.org/wiki |
|                |                |                | /Selkirkshire) |
|                |                |                | and small      |
|                |                |                | parts of       |
|                |                |                | [Midlothian]   |
|                |                |                | (https://en.wi |
|                |                |                | kipedia.org/wi |
|                |                |                | ki/Midlothian) |
|                |                |                | and            |
|                |                |                | [Ber           |
|                |                |                | wickshire](htt |
|                |                |                | ps://en.wikipe |
|                |                |                | dia.org/wiki/B |
|                |                |                | erwickshire)." |
|                |                |                |                |
|                |                |                | I chose 4 as a |
|                |                |                | denominator as |
|                |                |                | they represent |
|                |                |                | a "small part" |
|                |                |                | of the county  |
+----------------+----------------+----------------+----------------+
| Tweeddale      |                |                | The district   |
|                |                |                | which covered  |
|                |                |                | the            |
|                |                |                | [Sheriffdoms]  |
|                |                |                | (https://en.wi |
|                |                |                | kipedia.org/wi |
|                |                |                | ki/Sheriffdom) |
|                |                |                | of             |
|                |                |                | [Peebl         |
|                |                |                | es](https://en |
|                |                |                | .wikipedia.org |
|                |                |                | /wiki/Peebles) |
|                |                |                | and            |
|                |                |                | [Selkirk](     |
|                |                |                | https://en.wik |
|                |                |                | ipedia.org/wik |
|                |                |                | i/Selkirk,_Sco |
|                |                |                | ttish_Borders) |
|                |                |                | later became   |
|                |                |                | of the [County |
|                |                |                | of             |
|                |                |                | Peebles](h     |
|                |                |                | ttps://en.wiki |
|                |                |                | pedia.org/wiki |
|                |                |                | /Peeblesshire) |
|                |                |                | in the north   |
|                |                |                | and [County of |
|                |                |                | Selkirk](h     |
|                |                |                | ttps://en.wiki |
|                |                |                | pedia.org/wiki |
|                |                |                | /Selkirkshire) |
|                |                |                | or the         |
|                |                |                | **\"Ettrick    |
|                |                |                | Forest\"** in  |
|                |                |                | the south, two |
|                |                |                | of the         |
|                |                |                | [counties of   |
|                |                |                | Scotla         |
|                |                |                | nd](https://en |
|                |                |                | .wikipedia.org |
|                |                |                | /wiki/Counties |
|                |                |                | _of_Scotland). |
|                |                |                |                |
|                |                |                | Wikipedia      |
+----------------+----------------+----------------+----------------+
| Isle of Man    | Using 1934 and | From 1851 to   |                |
|                | not 1931       | 1891:          |                |
|                |                | [[             |                |
|                | I merge the    | http://www.isl |                |
|                | two different  | e-of-man.com/m |                |
|                | sources even   | anxnotebook/hi |                |
|                | if there are   | story/pop.htm] |                |
|                | small          | {.underline}]( |                |
|                | differences    | http://www.isl |                |
|                |                | e-of-man.com/m |                |
|                |                | anxnotebook/hi |                |
|                |                | story/pop.htm) |                |
|                |                |                |                |
|                |                | From 1934 to   |                |
|                |                | 2012           |                |
|                |                |                |                |
|                |                | [[htt          |                |
|                |                | ps://en.wikipe |                |
|                |                | dia.org/wiki/D |                |
|                |                | emographics\_o |                |
|                |                | f\_the\_Isle\_ |                |
|                |                | of\_Man]{.unde |                |
|                |                | rline}](https: |                |
|                |                | //en.wikipedia |                |
|                |                | .org/wiki/Demo |                |
|                |                | graphics_of_th |                |
|                |                | e_Isle_of_Man) |                |
+----------------+----------------+----------------+----------------+
| Vale of        | From : 1851 to |                | "Prior to 1974 |
| Glamorgan      | 1911:          |                | the area was   |
|                | [              |                | part of the    |
|                | [https://www.v |                | county of      |
|                | isionofbritain |                | [Glamorgan     |
|                | .org.uk/unit/1 |                | ](https://en.w |
|                | 0166550/cube/T |                | ikipedia.org/w |
|                | OT\_POP]{.unde |                | iki/Glamorgan) |
|                | rline}](https: |                | or             |
|                | //www.visionof |                | Gl             |
|                | britain.org.uk |                | amorganshire." |
|                | /unit/10166550 |                |                |
|                | /cube/TOT_POP) |                |                |
|                |                |                |                |
|                | From : 1851 to |                |                |
|                | 1911:          |                |                |
|                |                |                |                |
|                | [              |                |                |
|                | [https://www.v |                |                |
|                | isionofbritain |                |                |
|                | .org.uk/unit/1 |                |                |
|                | 0073893/cube/T |                |                |
|                | OT\_POP]{.unde |                |                |
|                | rline}](https: |                |                |
|                | //www.visionof |                |                |
|                | britain.org.uk |                |                |
|                | /unit/10073893 |                |                |
|                | /cube/TOT_POP) |                |                |
|                |                |                |                |
|                | Using 1934 and |                |                |
|                | not 1931       |                |                |
|                |                |                |                |
|                | Using 1942 and |                |                |
|                | not 1941       |                |                |
+----------------+----------------+----------------+----------------+
| Northern       | I use two      | https:/        |                |
| Ireland        | different      | /en.wikipedia. |                |
|                | sources on     | org/wiki/Demog |                |
|                | wiki page to   | raphy\_of\_Nor |                |
|                | complete       | thern\_Ireland |                |
|                | missing data   |                |                |
+----------------+----------------+----------------+----------------+
| West Glamorgan |                |                | Swansea+Neath  |
|                |                |                | Port Talbot    |
+----------------+----------------+----------------+----------------+
| Gwent          |                |                | Blaenau        |
|                |                |                | Gwent+         |
|                |                |                | Caerphilly/2+M |
|                |                |                | onmouthshire+N |
|                |                |                | ewport+Torfaen |
+----------------+----------------+----------------+----------------+
| Dyfed          |                |                | Carmarthensh   |
|                |                |                | ire+Ceredigion |
|                |                |                | +Pembrokeshire |
+----------------+----------------+----------------+----------------+
| Clwyd          |                |                | Fli            |
|                |                |                | ntshire+Wrexha |
|                |                |                | m+Denbighshire |
+----------------+----------------+----------------+----------------+
| South          |                |                | Vale of        |
| Glamorgan      |                |                | Gla            |
|                |                |                | morgan+Cardiff |
+----------------+----------------+----------------+----------------+
| Mid Glamorgan  |                |                | C              |
|                |                |                | aerphilly/2+Br |
|                |                |                | idgend+Merthyr |
|                |                |                | T              |
|                |                |                | ydfil+Rhondda; |
|                |                |                | Cynon; Taff    |
+----------------+----------------+----------------+----------------+
| Cheshire       |                |                | Halton+Warri   |
|                |                |                | ngton+Cheshire |
|                |                |                | east+Cheshire  |
|                |                |                | West and       |
|                |                |                | Chester        |
+----------------+----------------+----------------+----------------+
| Roxburgh       |                |                | Roxburghshir   |
| Ettrick and    |                |                | e+Selkirkshire |
| Lauderdale     |                |                | +Berwickshire/ |
|                |                |                | 4+Midlothian/4 |
|                |                |                |                |
|                |                |                | Divided by 4   |
|                |                |                | as small part  |
|                |                |                | of counties    |
|                |                |                | are concerned  |
+----------------+----------------+----------------+----------------+
| Tweeddale      |                |                | Peeble         |
|                |                |                | s+Selkirkshire |
+----------------+----------------+----------------+----------------+
| Northern       |                |                | No data for    |
| Ireland        |                |                | smaller        |
|                |                |                | entities, I    |
|                |                |                | supposed       |
|                |                |                | bounties were  |
|                |                |                | constant       |
+----------------+----------------+----------------+----------------+
| Inner London   |                |                | Camden + City  |
| --- West       |                |                | of London +    |
|                |                |                | Westminster    |
|                |                |                | +Kensington &  |
|                |                |                | Chelsea +      |
|                |                |                | Hammersmith &  |
|                |                |                | Fulham +       |
|                |                |                | Wandsworth     |
+----------------+----------------+----------------+----------------+
| Inner London   |                |                | Hackney +      |
| --- East       |                |                | Newham + Tower |
|                |                |                | Hamlets +      |
|                |                |                | Haringey +     |
|                |                |                | Islington +    |
|                |                |                | Lewisham +     |
|                |                |                | Southwark +    |
|                |                |                | Lambeth        |
+----------------+----------------+----------------+----------------+
| Outer London   |                |                | Bexley +       |
| --- East and   |                |                | Greenwich +    |
| North East     |                |                | Barking and    |
|                |                |                | Dagenham +     |
|                |                |                | Havering +     |
|                |                |                | Redbridge +    |
|                |                |                | Waltham Forest |
|                |                |                | + Enfield      |
+----------------+----------------+----------------+----------------+
| Outer London   |                |                | Bromley +      |
| --- South      |                |                | Croydon +      |
|                |                |                | Merton +       |
|                |                |                | Kingston upon  |
|                |                |                | Thames +       |
|                |                |                | Sutton         |
+----------------+----------------+----------------+----------------+
| Outer London   |                |                | Barnet + Brent |
| --- West and   |                |                | + Ealing +     |
| North West     |                |                | Harrow +       |
|                |                |                | Hillingdon +   |
|                |                |                | Hounslow +     |
|                |                |                | Richmond upon  |
|                |                |                | Thames         |
+----------------+----------------+----------------+----------------+

**Glossary:**

VoB= VisionofBritain (website)

Wiki= wikipedia

Wiki bis = particular section in wikipedia (e.g "Vital statistics" for
Northern Ireland)

Isle-of-Man =
[[http://www.isle-of-man.com/manxnotebook/history/pop.htm]{.underline}](http://www.isle-of-man.com/manxnotebook/history/pop.htm)

data.london=
[[https://data.london.gov.uk/dataset/historic-census-population]{.underline}](https://data.london.gov.uk/dataset/historic-census-population)
