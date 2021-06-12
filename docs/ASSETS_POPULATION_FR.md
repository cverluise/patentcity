This README documents the construction of population\_fr.csv from 1876
to 2018. This document reports the population of each FR county.

The data source is INSEE
[[https://www.insee.fr/fr/statistiques/3698339]{.underline}](https://www.insee.fr/fr/statistiques/3698339),
it provides population per town, I therefore aggregate per county
(département):

Data before 1876 are missing,
[[https://www.insee.fr/fr/statistiques/2659830?sommaire=2591397]{.underline}](https://www.insee.fr/fr/statistiques/2659830?sommaire=2591397)
data is incomplete and can't provide county population between 1800 and
1834.

R Code:

library(readr)

setcwd("your-project")

base\_pop\_historiques\_1876\_2018\_1 \<-
read\_csv(\"base-pop-historiques-1876-2018\_1.csv\")

df=base\_pop\_historiques\_1876\_2018\_1\[-c(1:4),-c(1,2,4)\]

colnames(df)\<-df\[1,\]

df=df\[-1,\]

install.packages(\"tidyverse\")

library(dplyr)

library(tidyr)

df1=df %\>%

pivot\_longer(starts\_with(\"population\_\"), names\_to = \"year\",
values\_to = \"population\", names\_prefix = \"population\_\")

df2=df1 %\>%

mutate(DEP=as.factor(DEP)) %\>%

mutate(population=as.numeric(population)) %\>%

group\_by(DEP, year) %\>%

summarise(population=sum(population))

df3=df2 %\>%

pivot\_wider(names\_from =\"year\",

values\_from =\"population\",

names\_prefix = \"pop\_\"

)

write.csv(df3, file = \"population\_fr.csv\")
