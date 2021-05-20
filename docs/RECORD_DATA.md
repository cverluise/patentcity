# DATA

> ℹ️ File names refer to data files in `gs://patentcity_dev/v1`

Name| Content | data
---|---|---
`*patentff.txt.tar.gz` | tar file containing format `ff` office `*` patents (`.txt` blobs) | List\[text\]
`*patentff.jsonl.gz` | jsonl file with format `ff` office `*` patents, to be used with `brew v1` | {"publication\_number": "", "text": "", "hash\_id": ""}
`entrel_*patentff.jsonl.gz` | jsonl files of extracted entities and relations from office `*` patents| {"publication_number":"", "patentee": [{}, {}]}
`entrelgeoc_*patentxx.jsonl.gz` | same but with geocoded data in addition| " "
`loc_*patentxx.txt_tmp.gz` | loc data (extracted from `entrel_*patentff.jsonl.gz`)| recId &#124; loc\_text
`loc_*patentxx.txt.gz` | same but wth prepared loc text | recId &#124; loc\_text
`loc_*patentxx.tbd.txt.gz` |loc data (preped) which has not been processed yet (ie tbd)| recId &#124; loc\_text
`loc_*patentxx.tbd.txt_rr.gz` |loc data (preped) to be processed at round `rr`| recId &#124; loc\_text
`loc_*patentxx.count.txt_tmp.gz` |loc data with their number of occurences| #occ recId &#124; loc\_text
`loc_*patentxx.count.txt.gz` | same but loc data preped | #occ recId &#124; loc\_text
`loc_*patentxx.sorted.txt.gz` | loc data (preped) unique and sorted by descending order of occurences| recId &#124; loc\_text
`loc_*patentxx.gmaps[here].txt_tmp.gz` |loc data sent to gmaps\[here\]| recId &#124; loc\_text
`loc_*patentxx.gmaps[here].txt.gz` |loc data (preped)sent to gmaps\[here\]| recId &#124; loc\_text
`geoc_*patentxx.gmaps.txt.gz` | geocoded data using GMAPS | `recId {gmaps output json}`
`geoc_*patentxx.gmaps[here].csv.gz` | geocoded data using GMAPS \[here\]& harmonized with HERE data structure| `,,,`
