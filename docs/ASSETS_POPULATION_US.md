This README documents the construction of population\_us.csv from 1831
to 2001. For the US, the right unit to analyze is the commuting zone in
order to have the same scale than french "département" or british
"counties".

Using Eckert,Gvirtz,Liang and Peters (2020) data, suppressed datas on
useless dates and associated each commuting zone code to his name.

R code:

library(readr)

pop\_cz \<- read.csv(\"C:/Users/Aymann/Downloads/pop\_cz.csv\",
header=FALSE)

county2cz \<- read.csv(\"C:/Users/Aymann/Downloads/county2cz.csv\")

county2cz=county2cz\[,-2\]

county2cz=unique(county2cz)

pop\_cz=pop\_cz\[,-c(2:5)\]

colnames(pop\_cz)\<-pop\_cz\[1,\]

pop\_cz=pop\_cz\[-1,\]

colnames(pop\_cz)\[1\]=\"cz\_num\"

colnames(county2cz)\[1\]=\"cz\_num\"

population\_us\_cz=merge(county2cz, pop\_cz, by =\"cz\_num\")

write.table(population\_us\_cz, \"population\_us\_cz.csv\",
row.names=FALSE, sep=\",\",dec=\".\", na=\" \")
