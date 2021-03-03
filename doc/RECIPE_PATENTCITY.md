# :cookie: Recipe

### Serialize data

> ℹ️ The below snippet shows the data serialization/brewing step where we extract entities from the raw texts.

#### get data

**option 1: preped data not available**

````shell
# get raw data
gsutil -m cp "gs://patentcity_dev/v1/*patent*.txt.tar.gz" ./ 

# Unpack data
cat lib/formats.txt | parallel --eta 'tar -xvzf {}.txt.tar.gz -C ./{}' 
# then, you can go for a week-end

# Prepare data
cat lib/formats.txt | parallel --eta -j 2 'patentcity brew v1.grind {}/*.txt >> {}.jsonl && gzip {}.jsonl'
````

**option 2: preped data available**

````shell
gsutil -m cp "gs://patentcity_dev/v1/*.jsonl.gz" ./
# should dl ddpatent01.jsonl.gz, ddpatent02.jsonl.gz, etc
````

#### extract patentees (and add topping)

```shell
# Extract entities (brew data)
cat lib/formats.txt | parallel --eta -j 3 'MODEL=$(ls -d models/**/model-best | grep {} ) && patentcity brew v1 {}.jsonl.gz ${MODEL} configs/rel_{}.yaml --batch-size 500 >> entrel_{}.jsonl'
# Number of job for a 8 CPUs 32Gb ram machine

# Merge all format belonging to the same office in one single file 
for OFFICE in  dd de fr gb us; do echo ${OFFICE} && cat entrel_${OFFICE}patent*.jsonl >> entrel_${OFFICE}patentxx.jsonl; done;

# Add topping 
ls entrel_*patentxx.jsonl | parallel --eta -j 2 'mv {} {}_tmp && patentcity brew v1.topping --cit-fst-file lib/cit_fst.json {}_tmp >> {} '
# Note: it can be memory greedy, you might want to limit the nb or jobs and/or the nb of workers

# Check output not corrupted
ls entrel_*patentxx.jsonl | parallel "wc -l {}*"
```

### Get loc data to be geocoded (all)

````shell
# Get loc data
ls entrel_*patentxx.jsonl |cut -d_ -f2 |  parallel --eta 'patentcity geo prep-geoc-data entrel_{} | sort -u >> loc_{.}.txt'

# Prep geoc data
ls loc_*patentxx.txt | parallel --eta 'mv {} {}_tmp && patentcity utils prep-searchtext {}_tmp configs/{.}.yaml >> {}'
````

### Restrict subset of loc data

#### Data that have not been geocoded yet (although some have already been)

````shell
# Below we assume that part of dataset has already been geocoded using gmaps (loc_*patentxx.gmaps.txt files) and we want  to geocode the rest (wrt the full list of loc in loc_*patentxx.txt) using HERE (in loc_*patentxx.tbd.txt).
ls loc_*patentxx.txt | parallel --eta 'comm -13 <(sort {.}.gmaps.txt) <(sort {}) >> {.}.tbd.txt'
````

#### Most reccurent loc

````shell
ls entrel_*patentxx.jsonl |cut -d_ -f2 |  parallel --eta 'patentcity geo prep-geoc-data entrel_{} | sort | uniq -c >> loc_{.}.count.txt'
ls loc_*patentxx.count.txt | cut -d. -f 1,2 | parallel --eta 'mv {}.txt {}.txt_tmp && patentcity utils prep-searchtext {}.txt_tmp configs/{.}.yaml >> {}.txt'
for FILE in $(ls loc_*patentxx.count.txt | cut -d. -f 1 ); do cat ${FILE}.count.txt | sort -nr  |awk '{$1=""; print $0}' | cut -c2- >> ${FILE}.sorted.txt; done;
# nb sorted in descending order

# Now assume that you want to get 250k addresses to geocode, covering as many occurences as possible and making sure that they have not been geocoded yet 
# Below, we get the 275k most cited addresses (unconditional) and we keep only those which are no yet done (ie in tbd as well)
# Nb requires a bit of fine tuning to make sure that we have the right nbr of lines:  rm -f tmp && head -n 275000 loc_${FORMAT}.sorted.txt >> tmp && comm -13 <(sort loc_${FORMAT}.tbd.txt) <(sort tmp) | wc -l    
FORMAT="uspatentxx"
rm -f tmp && head -n 275000 loc_${FORMAT}.sorted.txt >> tmp && comm -13 <(sort loc_${FORMAT}.tbd.txt) <(sort tmp) | sort -r >>  loc_${FORMAT}.tbd.txt_00
````

#### NOMATCH from HERE

````shell
ROUND="00"
for OFFICE in dd de fr gb us; do 
  patentcity utils get-recid-nomatch geoc_${OFFICE}patentxx.here.csv_${ROUND}.gz loc_${OFFICE}patentxx.tbd.txt_${ROUND} >> loc_${OFFICE}patentxx.tbd.nomatch.txt_${ROUND};
done;    
````


### Geocode dataset

> ℹ️ The below snippets walks you through the geocoding process.   

#### Using GMAPS

```shell
# Geocode using GMAPS
# 1-by-1
APIKEY=""
OFFICE=""  # see above 
REGION=""  # see above (nb uk for gb)
ROUND=""  # e.g. 00 
echo "OFFICE:${OFFICE} REGION:${REGION} ROUND:${ROUND}"
echo "loc_${OFFICE}patentxx.here.nomatch.txt_${ROUND} has $(wc -l loc_${OFFICE}patentxx.here.nomatch.txt_${ROUND}) line(s)"
# better safe than sorry
patentcity geo get-geoc-data-gmaps loc_${OFFICE}patentxx.here.nomatch.txt_${ROUND} ${APIKEY} ${REGION} >> geoc_${OFFICE}patentxx.gmaps.txt_${ROUND}
```

> ⚠️ Take care, geocoding is not free, especially using GMAPS. Keep calm and plan your budget, you might want to ask for a grant and/or chunk the data and process it month-by-month as you free-tier gets automatically refilled. You might also want to first start with the batch geocoding API from HERE (which offers much more generous free plan) and use gmaps only for the no-match. NB: HERE batch geocoding API is supported by patentcity.

#### using HERE

```shell
# Make sure that there is the appropriate header, ie recId|searchText
# if not, you can use sthg in the flavor of
# ls loc_*patentxx.tbd.txt_00* | parallel --eta 'mv {} {}_tmp && echo "recId|searchText" >> {} && cat {}_tmp >> {}'
APIKEY="" 
FILE="" # e.g. loc_ddpatentxx.tbd.txt_00
CNTFOCUS="" # e.g. deu

echo "FILE: ${FILE} CNTFOCUS: ${CNTFOCUS}"

patentcity geo post-geoc-data-here ${FILE} ${APIKEY} ${CNTFOCUS}
# print REQUESTID to stdout

# monitor status
REQUESTID=""
patentcity geo get-geoc-status-here $REQUESTID $APIKEY

# get data and rename
OUTPUTDIR="tmp"
mkdir -p ${OUTPUTDIR}
patentcity geo get-geoc-data-here ${REQUESTID} ${APIKEY} --output-dir ${OUTPUTDIR} && RESULT=$(ls ${OUTPUTDIR}/${REQUESTID}) && mv ${OUTPUTDIR}/${REQUESTID}/$RESULT ./"$(echo ${FILE} | sed -e 's/tbd/here/g; s/txt/csv/g; s/loc/geoc/g')" && echo "Saved as $(echo ${FILE} | sed -e 's/tbd/here/g; s/txt/csv/g; s/loc/geoc/g')!"
```

#### Using manual annotations (e.g. France)

**Generate manual annotations using Prodigy**

XX

**Generate manual annotations for country codes**
```shell
FORMAT = ""  # e.g. ddpatentxx
patentcity utils disamb-countrycodes loc_${FORMAT}.txt >> lib/loc_${FORMAT}.disamb.txt
```

```shell
FORMAT=""  # e.g. frpatentxx, ddpatentxx
DISAMBFILE=""  # e.g. lib/loc_${FORMAT}.disamb.txt
GEOCINDEX=""  # e.g. lib/geoc_${FORMAT}.disamb.index.txt lib/geoc_iso.disamb.index.txt 
FLAVOR=""  # HERE or GMAPS
patentcity geo add-geoc-disamb ${DISAMBFILE} ${GEOCINDEX} --flavor ${FLAVOR}>> geoc_${FORMAT}.manual.txt
# DISAMBFILE is a list of disambiguated loc together with their *original* hash (sep by the standard inDelim)
# GEOCINDEX is the list of geoc of disambigated loc (e.g. "république fédérale d'allemagne")
# FLAVOR is HERE or GMAPS depending on the flavor of GEOCINDEX  
# The output is a GMAPS like file (md5|{}) 
```

### Add geocoded data

```shell
# Harmonize GMAPS and MANUAL as HERE geocoded data
ls geoc_*patentxx.gmaps.txt.gz | cut -d. -f1,2 |parallel --eta 'patentcity geo harmonize-geoc-data-gmaps {}.txt.gz --out-format csv >> {}.csv && gzip {}.csv'
MANUALDISAMB="fr"
for OFFICE in ${MANUALDISAMB}; do
  patentcity geo harmonize-geoc-data-gmaps geoc_${OFFICE}patentxx.manual.txt --out-format csv >> geoc_${OFFICE}patentxx.manual.csv;
done;
  
# Incorporate geocoded data
# HERE and GMAPS
for OFFICE in dd de fr gb us; do
  echo ${OFFICE}
  patentcity geo add-geoc-data entrel_${OFFICE}patentxx.jsonl --geoc-file geoc_${OFFICE}patentxx.here.csv_00.gz --source HERE >> entrelgeoc_${OFFICE}patentxx.jsonl_tmp && 
  patentcity geo add-geoc-data entrelgeoc_${OFFICE}patentxx.jsonl_tmp --geoc-file geoc_${OFFICE}patentxx.gmaps.csv.gz --source GMAPS >> entrelgeoc_${OFFICE}patentxx.jsonl &&
  rm entrelgeoc_${OFFICE}patentxx.jsonl_tmp;
done;  

MANUALDISAMB="dd fr"  # we add dd which is already in HERE like format
for OFFICE in ${MANUALDISAMB}; do
  mv entrelgeoc_${OFFICE}patentxx.jsonl entrelgeoc_${OFFICE}patentxx.jsonl_tmp &&
  patentcity geo add-geoc-data entrelgeoc_${OFFICE}patentxx.jsonl_tmp --geoc-file geoc_${OFFICE}patentxx.manual.csv.gz --source MANUAL >> entrelgeoc_${OFFICE}patentxx.jsonl &&
  rm entrelgeoc_${OFFICE}patentxx.jsonl_tmp;
done;

for FILE in $(ls entrelgeoc_*patentxx.jsonl); do
 mv ${FILE} ${FILE}_tmp &&
 sed 's/\"seqNumber\":/\"loc_seqNumber\":/g; s/\"seqLength\":/\"loc_seqLength\":/g; s/\"latitude\":/\"loc_latitude\":/g; s/\"longitude\":/\"loc_longitude\":/g; s/\"locationLabel\":/\"loc_locationLabel\":/g; s/\"addressLines\":/\"loc_addressLines\":/g; s/\"street\":/\"loc_street\":/g; s/\"houseNumber\":/\"loc_houseNumber\":/g; s/\"building\":/\"loc_building\":/g; s/\"subdistrict\":/\"loc_subdistrict\":/g; s/\"district\":/\"loc_district\":/g; s/\"city\":/\"loc_city\":/g; s/\"postalCode\":/\"loc_postalCode\":/g; s/\"county\":/\"loc_county\":/g; s/\"state\":/\"loc_state\":/g; s/\"country\":/\"loc_country\":/g; s/\"relevance\":/\"loc_relevance\":/g; s/\"matchType\":/\"loc_matchType\":/g; s/\"matchCode\":/\"loc_matchCode\":/g; s/\"matchLevel\":/\"loc_matchLevel\":/g; s/\"matchQualityStreet\":/\"loc_matchQualityStreet\":/g; s/\"matchQualityHouseNumber\":/\"loc_matchQualityHouseNumber\":/g; s/\"matchQualityBuilding\":/\"loc_matchQualityBuilding\":/g; s/\"matchQualityDistrict\":/\"loc_matchQualityDistrict\":/g; s/\"matchQualityCity\":/\"loc_matchQualityCity\":/g; s/\"matchQualityPostalCode\":/\"loc_matchQualityPostalCode\":/g; s/\"matchQualityCounty\":/\"loc_matchQualityCounty\":/g; s/\"matchQualityState\":/\"loc_matchQualityState\":/g; s/\"matchQualityCountry\\r\":/\"loc_matchQualityCountry\":/g' ${FILE}_tmp >> ${FILE}
done; 
```

### Build data

```shell
STAGETABLE="patentcity:tmp.tmp"
RELEASETABLE="" # e.g. patentcity.tmp.tmp_100rc1
KEYFILE="" # e.g. credentials-patentcity.json
# Load data
bq load --source_format NEWLINE_DELIMITED_JSON --replace --ignore_unknown_values --max_bad_records 1000 ${STAGETABLE} "gs://patentcity_dev/v1/entrelgeoc_*patentxx.jsonl" schema/patentcity_v1.sm.json
# Augment data
patentcity io augment-patentcity $(echo ${STAGETABLE} | sed -e 's/:/./') ${RELEASETABLE} --key-file ${KEYFILE}

# Impute missing dates
#for OFFICE in dd de; do
#  patentcity utils expand-pubdate-imputation lib/pubdate_${OFFICE}patentxx.imputation.csv --output pubdate_${OFFICE}patentxx.imputation.expanded.csv;
#done;
# gsutil -m cp "pubdate_*patentxx.imputation.expanded.csv" gs://patentcity_dev/v1/

for OFFICE in dd de; do 
  bq load --source_format CSV --replace --ignore_unknown_values --max_bad_records 1000 patentcity:tmp.de_pubdate_imputation "gs://patentcity_dev/v1/pubdate_${OFFICE}patentxx.imputation.expanded.csv" schema/date_imputation.json
  patentcity io impute-publication-date ${RELEASETABLE} patentcity.tmp.${OFFICE}_pubdate_imputation --country-code ${OFFICE:u} --key-file ${KEYFILE};
done;    
```
