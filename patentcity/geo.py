"""
                            Patentcity geo

general principle: address (str) -> structured geo data (dict)
3 flavors: libpostal, HERE, GMAPS

# libpostal (parser)

Libpostal https://github.com/openvenues/libpostal
Docker libpostal https://github.com/johnlonganecker/libpostal-rest-docker
REST api https://github.com/johnlonganecker/libpostal-rest

Note: i) if set up on GCP, you need to set up firewall rules to authorize access from the requesting
machine ii) get external IP of GCP compute engine 
https://console.cloud.google.com/networking/addresses/list?project=<your-project>

# HERE Batch (geocoding)

Guide: developer.here.com/documentation/batch-geocoder/dev_guide/topics/request-constructing.html
API ref: https://developer.here.com/documentation/batch-geocoder/dev_guide/topics/endpoints.html

# Gmaps (geocoding)

API ref

- https://developers.google.com/maps/documentation/geocoding/start
- https://developers.google.com/maps/documentation/geocoding/overview
"""


import csv
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from glob import glob
from itertools import repeat
from zipfile import ZipFile

import googlemaps
import pandas as pd
import requests
import typer
from bs4 import BeautifulSoup
from smart_open import open  # pylint: disable=redefined-builtin

from patentcity.lib import (
    GEOC_OUTCOLS,
    GEOC_URL,
    HERE2GMAPS,
    TYPE2LEVEL,
    get_countycrossover,
    get_isocrossover,
    get_usstatecrossover,
)
from patentcity.utils import (
    clean_text,
    flatten,
    get_dt_human,
    get_empty_here_schema,
    get_recid,
    not_ok,
    ok,
    read_csv_many,
)

app = typer.Typer()


def _parse_loc_blob(line, api_reference, debug):
    """Return the line with parsed LOCs"""

    def get_parsed_loc_blob(loc, api_reference, debug):
        """Request http://api_reference/parser with query loc"""
        data = json.dumps({"query": clean_text(loc)})
        response = requests.post(f"http://{api_reference}/parser", data=data)
        if debug and response.status_code != 200:
            typer.secho(
                f"{loc} failed with status code {response.status_code}",
                fg=typer.colors.RED,
            )
        return json.loads(response.text)

    def flatten_parsed_loc(parsed_loc):
        """Flatten the libpostal response"""
        out = {}
        for e in parsed_loc:
            out.update({e["label"]: e["value"]})
        return out

    line = json.loads(line)
    locs = line.get("loc")
    if locs:
        locs_ = []
        for loc in locs:
            parsed_loc = get_parsed_loc_blob(loc, api_reference, debug)
            parsed_loc = flatten_parsed_loc(parsed_loc)
            parsed_loc.update({"raw": loc})
            locs_ += [parsed_loc]
        line.update({"loc": locs_})
    typer.echo(json.dumps(line))


@app.command(deprecated=True, name="libpostal.get")
def get_parsed_loc_libpostal(
    path: str, api_reference: str, max_workers: int = 10, debug: bool = False
):
    """
    Send data in `path` to libpostal service (hosted at `api_reference`)
    and return parsed loc json blobs to stdout.

    Arguments:
        path: data path (wildcard allowed)
        api_reference: reference of service host "ip:port"
        max_workers: max number of workers
        debug: verbosity degree

    **Usage:**
        ```shell
        patentcity geo libpostal.get <your-addresses.txt> <ip:port>
        ```
    """
    files = glob(path)
    for file in files:
        data = open(file, "r")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            executor.map(_parse_loc_blob, data, repeat(api_reference), repeat(debug))


@app.command(name="here.post")
def post_geoc_data_here(
    file: str,
    api_key: str,
    countryfocus: str,  # ISO3?
    outCols: str = None,  # pylint: disable=invalid-name
    inDelim: str = "|",  # pylint: disable=invalid-name
    outDelim: str = ",",  # pylint: disable=invalid-name
    locationattributes: str = "addressDetails",
    language: str = "en-EN",  # eg "en-EN", "en-US"
    includeinputfields: bool = False,  # False for downstream compatibility
    verbose: bool = False,
):
    """Post `file` to HERE batch geocoding API

    Arguments:
        file: file path. File is expected to be formatted as follows recId|searchText
        api_key: HERE api key
        countryfocus: iso3 country code (e.g. deu, fra, gbr, usa, etc), see [Format input](https://developer.here.com/documentation/batch-geocoder/dev_guide/topics/data-input.html)
        outCols: see [Request parameters](https://developer.here.com/documentation/batch-geocoder/dev_guide/topics/request-parameters.html)
        inDelim: see [Request parameters](https://developer.here.com/documentation/batch-geocoder/dev_guide/topics/request-parameters.html)
        outDelim: see [Request parameters](https://developer.here.com/documentation/batch-geocoder/dev_guide/topics/request-parameters.html)
        locationattributes: see [Request parameters](https://developer.here.com/documentation/batch-geocoder/dev_guide/topics/request-parameters.html)
        language: output language, see [Request parameters](https://developer.here.com/documentation/batch-geocoder/dev_guide/topics/request-parameters.html)
        includeinputfields: see [Request parameters](https://developer.here.com/documentation/batch-geocoder/dev_guide/topics/request-parameters.html)
        verbose: verbosity

    **Usage:**
        ```shell
        patentcity geo here.post loc_uspatentxx.txt $APIKEY usa
        ```

    !!! info
        - [Format input](https://developer.here.com/documentation/batch-geocoder/dev_guide/topics/data-input.html)
        - [Request parameters](https://developer.here.com/documentation/batch-geocoder/dev_guide/topics/request-parameters.html)
    """

    def check_post(response):
        soup = BeautifulSoup(response.text, features="xml")
        RequestId = soup.RequestId.text
        Status = soup.Status.text
        log_msg = f"{file}\t{Status}\t{RequestId}\t{get_dt_human()}"
        if verbose:
            typer.echo(soup.prettify())
        if Status == "accepted":
            typer.secho(f"{ok}{log_msg}", fg=typer.colors.GREEN)
        else:
            typer.secho(f"{not_ok}\t{log_msg}", fg=typer.colors.RED)

    headers = {"Content-Type": "text/plain"}
    outCols = outCols.split(",") if outCols else GEOC_OUTCOLS

    # Remove default columns to avoid duplicated columns
    for col in ["recID", "seqNumber", "seqLength"]:
        try:
            outCols.remove(col)
        except ValueError:
            pass

    params = (
        ("apiKey", api_key),
        ("action", "run"),
        ("header", "true"),
        ("inDelim", inDelim),
        ("outDelim", outDelim),
        ("outCols", ",".join(outCols)),
        ("outputcombined", "true"),
        ("countryfocus", countryfocus),
        ("language", language),
        ("locationattributes", locationattributes),
        ("includeinputfields", includeinputfields),
    )

    data = open(file, "rb").read()
    response = requests.post(GEOC_URL, headers=headers, params=params, data=data)
    if response.status_code == 200:
        check_post(response)
    else:
        typer.secho(
            f"{not_ok}Failed with status {response.status_code}\n{response.content}",
            fg=typer.colors.RED,
        )


@app.command(name="here.status")
def get_geoc_status_here(
    request_id: str, api_key: str, freq: int = 5, verbose: bool = False
):
    """Check status of job `request_id` every `freq` seconds

    Arguments:
        request_id: HERE job request ID (returned by `here.post)
        api_key: HERE api key
        freq: interval between 2 consecutive status updates
        verbose: verbosity

    **Usage:**
        ```shell
        patentcity geo here.status $REQUESTID $APIKEY
        ```
    """

    def summarize_status(response, verbose):
        soup = BeautifulSoup(response.text, "xml")
        now = get_dt_human()
        Status = soup.Status.text
        TotalCount = soup.TotalCount.text
        ProcessedCount = soup.ProcessedCount.text
        PendingCount = soup.PendingCount.text
        ErrorCount = soup.ErrorCount.text
        SuccessCount = soup.SuccessCount.text
        typer.secho(
            f"{now}: {ProcessedCount}/{TotalCount} ({PendingCount} pending)",
            fg=typer.colors.BLUE,
        )
        if int(SuccessCount) > 0:
            typer.secho(
                f"{ok}{SuccessCount} addresses successfully geocoded",
                fg=typer.colors.GREEN,
            )
        if int(ErrorCount) > 0:
            typer.secho(f"{not_ok}{ErrorCount} errors detected", fg=typer.colors.RED)
        if verbose:
            typer.echo(soup.prettify())
        return Status

    params = (("action", "status"), ("apiKey", api_key))
    completed = False
    while not completed:
        response = requests.get(f"{GEOC_URL}/{request_id}", params=params)
        Status = summarize_status(response, verbose)
        if Status == "completed":
            completed = True
            typer.secho(f"{ok}{ok}Job completed", fg=typer.colors.GREEN)
        else:
            typer.secho(f"Status:{Status}", fg=typer.colors.BLUE)
            time.sleep(freq)


@app.command(name="here.get")
def get_geoc_data_here(
    request_id: str, api_key: str, output_dir: str = None, unzip: bool = True
):
    """Download and save HERE geocoded data to `output_dir`/`request_id`.zip

    Arguments:
        request_id: HERE job request ID (returned by `here.post)
        api_key: HERE api key
        output_dir: saving directory
        unzip: whether to unzip the output

    **Usage:**
        ```shell
        patentcity geo here.get $REQUESTID $APIKEY --output-dir <your-dir>
        ```

    !!! info
        - [Read output](https://developer.here.com/documentation/batch-geocoder/dev_guide/topics/read-batch-request-output.html)
    """

    def dump_data(response, output_file):
        with open(output_file, "wb") as fout:
            fout.write(response.content)
            typer.secho(f"{ok}{output_file}", fg=typer.colors.GREEN)

    def unzip_data(zip_file):
        unzip_dir = os.path.splitext(zip_file)[0]
        with ZipFile(zip_file, "r") as zipObj:
            # Extract all the contents of zip file in different directory
            zipObj.extractall(unzip_dir)
            typer.secho(f"{ok}{zip_file} unzipped", fg=typer.colors.GREEN)

    output_file = os.path.join(output_dir, f"{request_id}.zip")
    params = (("apiKey", api_key),)
    response = requests.get(
        f"https://batch.geocoder.ls.hereapi.com/6.2/jobs/{request_id}/result/",
        params=params,
    )
    if response.status_code == 200:
        dump_data(response, output_file)
        if unzip:
            unzip_data(output_file)
    else:
        typer.secho(
            f"{not_ok}Failed with status {response.status_code}\n{response.content}",
            fg=typer.colors.RED,
        )
    # return response


@app.command(name="prep")
def prep_geoc_data(file: str, inDelim: str = "|"):
    """Return patentees' loc data formatted for geocoding to stdout (recId|searchText).

    Arguments:
        file: file path
        inDelim: inner delimiter used by HERE

    **Usage:**
        ```shell
        patentcity geo prep entrel_uspatent01.jsonl
        #Sort and deduplicate addresses before batch geocoding
        sort -u loc_uspatent01.txt
        ```
    """
    with open(file, "r") as lines:
        typer.echo(f"recId{inDelim}searchText")  # This is the required header
        for line in lines:
            line = json.loads(line)
            patentees = line.get("patentee")
            for patentee in patentees:
                loc_recid = patentee.get("loc_recId")
                loc_text = patentee.get("loc_text")
                if loc_recid and loc_text:
                    typer.echo(f"{loc_recid}{inDelim}{loc_text}")


# @app.command()
def _get_geoc_index(file: str, outDelim: str = ",", dump: bool = True):
    """Create index of here results
    {"recId-1":{"latitude":"","longitude":"",...},
     "recId-2":{"latitude":"","longitude":"",...},
      ...}"""

    def get_header(file, outDelim: str = ","):
        with open(file, "r") as lines:
            for line in lines:
                header = line.replace("\n", "").split(outDelim)
                break
            return header

    header = get_header(file, outDelim)
    index = {}
    with open(file, "r") as fin:
        csv_reader = csv.DictReader(fin, fieldnames=header)
        for i, line in enumerate(csv_reader):
            if i > 0:
                line = dict(line)
                seqNumber = (
                    line.get("SeqNumber")
                    if line.get("SeqNumber")
                    else line.get("seqNumber")
                )
                if int(seqNumber) > 1:
                    # we keep only the first proposed item
                    # TODO evaluate policy
                    pass
                else:
                    recid = line[
                        "recId"
                    ]  # make sure that this is an int - no more needed
                    line.pop("recId")
                    if line.get("SeqNumber"):
                        # causes conflict in BQ which is NOT case-sensitive
                        line.pop("SeqNumber")
                    index.update({recid: line})
    if dump:
        fname = ".".join([os.path.splitext(file)[0], "json"])
        with open(fname, "w") as fout:
            fout.write(json.dumps(index))
            typer.secho(f"{ok}{fname}")
    else:  # for internal use
        return index


def _update_loc(blob, source, index, verbose):
    blob = json.loads(blob)
    patentees_ = []
    patentees = blob.get("patentee")
    if patentees:
        for patentee in patentees:
            loc_recid = patentee.get("loc_recId")
            if loc_recid:
                geoc_ = index.get(loc_recid)
                if geoc_:
                    patentee.update(geoc_)
                    patentee.update({"loc_source": source})
                else:
                    if verbose:
                        typer.secho(
                            f"{not_ok}{loc_recid} ({type(loc_recid)}) not found",
                            fg=typer.colors.RED,
                        )
            patentees_ += [patentee]
        blob.update({"patentee": patentees_})
    typer.echo(json.dumps(blob))


@app.command(name="add")
def add_geoc_data(
    file: str,
    geoc_file: str,
    source: str = None,
    max_workers: int = 5,
    verbose: bool = False,
):
    """Add geoc data from `geoc_file`to `file`

    Arguments:
        file: file path
        geoc_file: geoc file path (geocoding output, csv)
        source: geocoding service (in ["HERE", "GMAPS", "MANUAL"])
        max_workers: max number of workers
        verbose: verbosity

    **Usage:**
        ```shell
        patentcity geo add entrel_uspatentxx.jsonl geoc_uspatentxx.here.csv --source HERE
        ```
    """
    assert source in ["GMAPS", "HERE", "MANUAL"]
    index = _get_geoc_index(geoc_file, dump=False)
    blobs = open(file, "r")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(_update_loc, blobs, repeat(source), repeat(index), repeat(verbose))


def _get_geoc_data_gmaps(line, gmaps_client, region, language, inDelim):
    recid, searchtext = line.split(inDelim)
    res = gmaps_client.geocode(searchtext, region=region, language=language)
    typer.echo(f"{recid}{inDelim}{json.dumps(res)}")


@app.command(name="gmaps.get")
def get_geoc_data_gmaps(
    file: str,
    api_key: str,
    region: str,
    language: str = "en",
    max_workers: int = 5,
    inDelim: str = "|",
    skip_header: bool = True,
):
    """Geocode addresses in `file` using GMAPS

    Arguments:
        file: file path
        api_key: api key
        region:  region code, specified as a ccTLD (“top-level domain”) two-character value (e.g. de, fr, uk, us, etc).
        language: the language in which to return results
        max_workers: max number of workers
        inDelim: inner delimiter
        skip_header: whether to ski header or not

    **Usage:**
        ```shell
        patentcity geo gmaps.get loc_uspatentxx.txt $APIKEY us
        ```

    !!! info
        - [Quickstart](https://developers.google.com/maps/documentation/geocoding/start)
        - [Overview](https://developers.google.com/maps/documentation/geocoding/overview)
        - [Language](https://developers.google.com/maps/faq#languagesupport)
    """
    gmaps = googlemaps.Client(api_key)
    with open(file, "r") as lines:
        if skip_header:
            next(lines)
        with ThreadPoolExecutor(max_workers) as executor:
            executor.map(
                _get_geoc_data_gmaps,
                lines,
                repeat(gmaps),
                repeat(region),
                repeat(language),
                repeat(inDelim),
            )


def _parse_response_gmaps(  # pylint: disable=too-many-statements
    response, recid, out_format, iso_crossover, us_state_crossover, county_crossover
):
    """Parse the high level Gmaps response (list of results). Can contain more than 1 results as
    well as 0."""

    def parse_result_gmaps(result, recid, seqNumber):
        """Parse Gmaps result. Note: not harmonization"""
        res = {}
        for kind in ["long_name", "short_name"]:
            address_components = flatten(
                [
                    [
                        {f"{component['types'][typ]}_{kind}": component[kind]}
                        for typ in range(len(component["types"]))
                    ]
                    for component in result["address_components"]
                ]
            )
            for address_component in address_components:
                res.update(address_component)
        res.update(result["geometry"]["location"])
        res.update({"location_type": result["geometry"]["location_type"]})
        res.update({"formatted_address": result["formatted_address"]})
        res.update({"recId": recid})
        res.update({"seqNumber": seqNumber})
        res.update({"types": result["types"]})
        return res

    def types2level_crossover(types):
        """Return a matchLevel (str, HERE flavor) based on types (list, GMAPS)"""

        def min_geoent(levels):
            level = None
            if levels:
                if "houseNumber" in levels:
                    level = "houseNumber"
                elif "street" in levels:
                    level = "street"
                elif "district" in levels:
                    level = "district"
                elif "postalCode" in levels:
                    level = "postalCode"
                elif "city" in levels:
                    level = "city"
                elif "county" in levels:
                    level = "county"
                elif "state" in levels:
                    level = "state"
                elif "country" in levels:
                    level = "country"
                else:
                    level = None
            return level

        levels = []
        for type_ in types:
            levels += [TYPE2LEVEL.get(type_)]
        levels = list(set(filter(lambda x: x, levels)))
        level = min_geoent(levels)
        return level

    def emulate_nomatch_gmaps(recid):
        out = get_empty_here_schema()
        out.update({"recId": recid, "seqNumber": 0, "matchLevel": "NOMATCH"})
        return out

    def flush_result(out, out_format):
        if out_format == "csv":
            csvwriter = csv.DictWriter(sys.stdout, GEOC_OUTCOLS)
            csvwriter.writerow(out)
        else:
            typer.echo(json.dumps(out))

    response = json.loads(response)

    if response:
        for seqNumber, result in enumerate(response):
            res = parse_result_gmaps(result, recid, seqNumber + 1)
            # seqNumber starts from 1. 0 is for NOMATCH
            out = get_empty_here_schema()
            # from now on, we harmonize output with HERE
            for k, _ in out.items():
                out.update({k: res.get(HERE2GMAPS[k])})
            # iso 2 to iso 3 (align gmaps (ISO2) on HERE (ISO3))
            out.update({"country": iso_crossover.get(out.get("country"))})
            # US state to code form
            out.update(
                {"state": us_state_crossover.get(out.get("state"), out.get("state"))}
            )
            # county 'harmonization'
            if out.get("country") == "USA" and out.get("county"):
                county_ = (
                    out.get("county")
                    .replace("County", "")
                    .replace("Parish", "")
                    .replace("Borough", "")
                    .replace("Census Area", "")
                    .replace("St.", "St")
                    .replace("Ste.", "Ste")
                    .replace("'s", "s")
                    .strip()
                )
                out.update({"county": county_})
            county_ = county_crossover.get(out.get("county"), out.get("county"))
            out.update({"county": county_})
            # matchLevel harmonization
            out.update({"matchLevel": types2level_crossover(out["matchLevel"])})
            if not out.get("latitude"):
                # in case there is no coordinates in the result, it's a NOMATCH
                out = emulate_nomatch_gmaps(recid)
            flush_result(out, out_format)
    else:
        out = emulate_nomatch_gmaps(recid)
        flush_result(out, out_format)


@app.command(name="gmaps.harmonize")
def harmonize_geoc_data_gmaps(
    file: str, inDelim: str = "|", out_format: str = "csv", header: bool = True
):
    """Harmonize Gmaps response with HERE Geocoding API responses (csv)

    Arguments:
        file: file path
        inDelim: inner delimiter
        out_format: format of the output (in ["csv", "jsonl"])
        header: whether to add a header (if `out_format` is "csv")

    **Usage:**
        ```shell
        patentcity geo gmaps.harmonize geoc_uspatentxx.gmaps.jsonl
        ```
    """

    assert out_format in ["csv", "jsonl"]
    iso_crossover = get_isocrossover()
    us_state_crossover = get_usstatecrossover()
    county_crossover = get_countycrossover()

    if out_format == "csv" and header:
        csvwriter = csv.DictWriter(sys.stdout, GEOC_OUTCOLS)
        csvwriter.writeheader()

    with open(file, "r") as lines:
        for line in lines:
            line = clean_text(line, inDelim=f" {inDelim} ")
            # clean cases like "Jack A. Claes Pavilion | Elk Grove Park District" returned by Gmaps

            try:
                recid, response = line.split(inDelim)
                _parse_response_gmaps(
                    response,
                    recid,
                    out_format,
                    iso_crossover,
                    us_state_crossover,
                    county_crossover,
                )
            except ValueError:
                pass
                # occurs when there is still an inDelim in the result
                # (e.g. "long_name": "S2|02 Robert-Piloty-Geb\u00e4ude")


@app.command(name="add.disamb")
def add_geoc_disamb(
    disamb_file: str, index_geoc_file: str, flavor: str = "GMAPS", inDelim: str = "|"
):
    """Return a list of recId|geoc(target) from a list of recid|target.

    Arguments:
        disamb_file: disambiguation data file path
        index_geoc_file: index geocoding file path
        flavor: flavor of `index_geoc_file` (in ["HERE","GMAPS"])
        inDelim: inner delimiter

    **Usage:**
        ```shell
        patentcity geo add.disamb ${DISAMBFILE} ${GEOCINDEX} --flavor ${FLAVOR}
        ```

    !!! info
        Use before `patentcity geo add`
    """
    assert flavor in ["GMAPS", "HERE"]
    if flavor == "GMAPS":
        index = {}
        with open(index_geoc_file, "r") as lines:
            for line in lines:
                recid, geoc = line.split(inDelim)
                index.update({recid: json.loads(geoc)})

        with open(disamb_file, "r") as lines:
            for line in lines:
                recid, disamb_loc = line.split(inDelim)
                disamb_loc_recid = get_recid(clean_text(disamb_loc))
                typer.echo(f"{recid}{inDelim}{json.dumps(index.get(disamb_loc_recid))}")
    else:
        index = _get_geoc_index(index_geoc_file, dump=False)
        fieldnames = GEOC_OUTCOLS
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        with open(disamb_file, "r") as lines:
            for line in lines:
                recid, searchtext = line.replace("\n", "").split(inDelim)
                geoc_disamb = index.get(get_recid(searchtext))
                geoc_disamb.update({"recId": recid})
                writer.writerow(geoc_disamb)


def get_statisticalarea_key(x):
    def prep_us_key(x):
        state, county, city = x
        if state and county:
            key = ".".join([state, county.replace(" ", "")])
        elif state and city:
            key = ".".join([state, city.replace(" ", "")])
        else:
            key = None
        return key

    country, state, county, city, postal_code = x
    if country in ["DEU", "FRA", "GBR", "USA"]:
        if country == "USA":
            key = prep_us_key((state, county, city))
        else:
            key = postal_code
    else:
        key = None
    return key


@app.command(name="add.statisticalareas")
def add_statisticalareas(file: str, statisticalareas_path: str, verbose: bool = False):
    """Return `file` with statistical areas to stdout.

    Arguments:
         file: file path
         statisticalareas_path: satistical area files path (wildcard allowed)
         verbose: verbosity

    **Usage:**
        ```shell
        patentcity geo add.statisticalareas geoc_gbpatentxx.here.csv "assets/statisticalareas_*.csv"
        ```
    """
    statisticalareas_df = read_csv_many(
        statisticalareas_path, verbose=verbose, dtype=str
    )
    geoc_df = pd.read_csv(file, dtype=str, error_bad_lines=False)
    geoc_df = geoc_df.where(pd.notnull(geoc_df), None)  # we replace pandas nan by None
    variables = ["country", "state", "county", "city", "postalCode"]
    geoc_df["key"] = geoc_df[variables].apply(get_statisticalarea_key, axis=1)
    geoc_df = geoc_df.merge(statisticalareas_df, how="left", on=["country", "key"])
    typer.echo(geoc_df.to_csv(sys.stdout, index=False))


if __name__ == "__main__":
    app()
