# DATE IMPUTATION

## Problem

Before 1919 (incl), the publication date of DE patents is missing.
Frontier is fuzzy, patents publication numbers are not exactly chronological but nearly. This makes it hard to manually find the latest publication number for each vintage. Number seem to be given based on the "Patentdatum"

## Approach

We look in the corpus of patents to find the latest publication number for each given year from 1877 to 1920.
We use the patent gazette published par the German patent offices ("PatentBlat") and consider the largest publication number specified under section "Erteilungen". The gazette is published weekly and we consider either week 52 or week 53 of each year from 1878 to 1919 (and 51 for 1918).
From these benchmark patents, we carry forward the year of publication.

!!! warning
    This method is not applicable for patents published earlier than 1883, hence for years 1877-1882, we manually look for patents with publication date in late December and arbitrarily select a benchmark.


## Results

| Publication year | Benchmark publication number                               |
| ---------------- | ---------------------------------------------------------- |
| 1877             | DE-1877-C*                                                 |
| 1878             | DE-3297-C*                                                 |
| 1879             | DE-8460-C*                                                 |
| 1880             | DE-12116-C*                                                |
| 1881             | DE-16547-C*                                                |
| 1882             | DE-20544-C*                                                |
| 1883             | DE-26025-C                                                 |
| 1884             | DE-30543-C                                                 |
| 1885             | DE-34561-C                                                 |
| 1886             | DE-38569-C                                                 |
| 1887             | DE-42451-C                                                 |
| 1888             | DE-46348-C                                                 |
| 1889             | DE-50707-C                                                 |
| 1890             | DE-55460-C                                                 |
| 1891             | DE-61010-C                                                 |
| 1892             | DE-66910-C                                                 |
| 1893             | DE-73340-C                                                 |
| 1894             | DE-79528-C                                                 |
| 1895             | DE-85240-C                                                 |
| 1896             | DE-90750-C                                                 |
| 1897             | DE-96190-C                                                 |
| 1898             | DE-101760-C                                                |
| 1899             | DE-109190-C (we use DE-109189-C as DE-109190-C is missing) |
| 1900             | DE-117765-C                                                |
| 1901             | DE-128268-C                                                |
| 1902             | DE-139092-C                                                |
| 1903             | DE-149056-C                                                |
| 1904             | DE-158245-C                                                |
| 1905             | DE-167845-C                                                |
| 1906             | DE-180900-C                                                |
| 1907             | DE-194320-C                                                |
| 1908             | DE-206135-C                                                |
| 1909             | DE-218130-C                                                |
| 1910             | DE-230230-C                                                |
| 1911             | DE-242870-C                                                |
| 1912             | DE-255770-C                                                |
| 1913             | DE-269260-C                                                |
| 1914             | DE-281820-C                                                |
| 1915             | DE-290010-C                                                |
| 1916             | DE-296016-C                                                |
| 1917             | DE-303620-C                                                |
| 1918             | DE-310930-C                                                |
| 1919             | DE-318790-C                                                |
