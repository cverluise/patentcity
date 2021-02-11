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
import requests
import typer
from bs4 import BeautifulSoup

from patentcity.lib import (
    GEOC_URL,
    GEOC_OUTCOLS,
    HERE2GMAPS,
    get_isocrossover,
    TYPE2LEVEL,
)
from patentcity.utils import clean_text, get_dt_human, get_empty_here_schema, flatten
from patentcity.utils import ok, not_ok, get_recid

"""
                              Parse LOC using libpostal
Libpostal https://github.com/openvenues/libpostal
Docker libpostal https://github.com/johnlonganecker/libpostal-rest-docker
REST api https://github.com/johnlonganecker/libpostal-rest
Note:
- if set up on GCP, you need to set up firewall rules to authorize access from the requesting
machine
- get external IP of GCP compute engine https://console.cloud.google.com/networking/addresses/list
?project=<your-project>
Then, to build on BigQuery, use schema/xx_entpars_*.json

                          Geocode LOC using HERE Batch geocoding API
Guide: developer.here.com/documentation/batch-geocoder/dev_guide/topics/request-constructing.html
API ref: https://developer.here.com/documentation/batch-geocoder/dev_guide/topics/endpoints.html

                            Geocode LOC using Gmaps geocoding API
API ref
- https://developers.google.com/maps/documentation/geocoding/start
- https://developers.google.com/maps/documentation/geocoding/overview
"""

app = typer.Typer()


def parse_loc_blob(line, api_reference, debug):
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


@app.command(deprecated=True)
def get_parsed_loc(
    path: str,
    api_reference: str = typer.Argument(..., help="ip:port"),
    max_workers: int = 10,
    debug: bool = False,
):
    """Print json blobs with parsed loc to stdout"""
    files = glob(path)
    for file in files:
        data = open(file, "r")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            executor.map(parse_loc_blob, data, repeat(api_reference), repeat(debug))


@app.command()
def post_geoc_data_here(
    file: str,
    api_key: str,
    countryfocus: str,  # ISO3?
    outCols: str = None,
    inDelim: str = "|",
    outDelim: str = ",",
    locationattributes: str = "addressDetails",
    language: str = "en-EN",  # eg "en-EN", "en-US"
    includeinputfields: bool = False,  # False for downstream compatibility
    verbose: bool = False,
):
    """Post <data> to HERE batch geocoding API (recId|searchText)

    Format input:
    developer.here.com/documentation/batch-geocoder/dev_guide/topics/data-input.html
    Request parameters:
    developer.here.com/documentation/batch-geocoder/dev_guide/topics/request-parameters.html
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
        ("", ""),
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


@app.command()
def get_geoc_status_here(
    request_id: str, api_key: str, freq: int = 5, verbose: bool = False
):
    """Check status of job <request_id>"""

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


@app.command()
def get_geoc_data_here(
    request_id: str, api_key: str, output_dir: str = None, unzip: bool = True
):
    """Save geocoded data to <output_dir>/<request_id>.zip

    Read output:
    developer.here.com/documentation/batch-geocoder/dev_guide/topics/read-batch-request-output.html
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


@app.command()
def prep_geoc_data(file: str, inDelim: str = "|"):
    """Write material for batch geocoding using HERE API to stdout. Receive a jsonl file.

    Run $sort -n -u <output-file.txt> >> <your-file.txt> to sort and deduplicate addresses before
    batch geocoding."""
    with open(file, "r") as lines:
        typer.echo(f"recId{inDelim}searchText")  # This is the required header
        for line in lines:  # iterate over file lines {"loc":[{""},{}],...}
            line = json.loads(line)
            patentees = line.get("patentee")
            for patentee in patentees:
                loc_recid = patentee.get("loc_recId")
                loc_text = patentee.get("loc_text")
                if loc_recid and loc_text:
                    typer.echo(f"{loc_recid}{inDelim}{loc_text}")


# @app.command()
def get_geoc_index(file: str, outDelim: str = ",", dump: bool = True):
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


def update_loc(blob, source, index, verbose):
    blob = json.loads(blob)
    locs = blob.get("loc")

    if locs:
        locs = []
        for loc_ in blob["loc"]:
            # loc is a list of dict with the following form
            # [{"raw":"", "recId":""},...]
            recid = loc_["recId"]  # int no more needed
            geoc_ = index.get(recid)
            if geoc_:
                loc_.update(geoc_)
                loc_.update({"source": source})
            else:
                if verbose:
                    typer.secho(
                        f"{not_ok}{recid} ({type(recid)}) not found",
                        fg=typer.colors.RED,
                    )
            locs += [loc_]
            # loc is now a list of dict with the following form
            # [{"raw":"", "recId":"", "longitude":"", "latitude":"",},...]
        blob.update({"loc": locs})
    typer.echo(json.dumps(blob))


@app.command()
def add_geoc_data(
    src,
    geoc_file: str = None,
    source: str = None,
    max_workers: int = 5,
    verbose: bool = False,
):
    """Add geoc data from geoc_file returned by HERE batch geocoding API"""
    assert source in ["GMAPS", "HERE", "MANUAL"]
    index = get_geoc_index(geoc_file, dump=False)
    blobs = open(src, "r")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(update_loc, blobs, repeat(source), repeat(index), repeat(verbose))


def get_geoc_data_gmap_(line, gmaps_client, region, language, inDelim):
    recid, searchtext = line.split(inDelim)
    res = gmaps_client.geocode(searchtext, region=region, language=language)
    typer.echo(f"{recid}{inDelim}{json.dumps(res)}")


@app.command()
def get_geoc_data_gmaps(
    file,
    key,
    region: str,
    language: str = "en",
    max_workers: int = 5,
    inDelim: str = "|",
    skip_header: bool = True,
):
    """
    Return the gmaps geocoding response

    region:  The region code, specified as a ccTLD (“top-level domain”) two-character
    value (e.g. en, us, de, fr).
    language: the language in which to return results

    Doc:
    - https://developers.google.com/maps/documentation/geocoding/start
    - https://developers.google.com/maps/documentation/geocoding/overview
    - https://developers.google.com/maps/faq#languagesupport
    """
    gmaps = googlemaps.Client(key)
    with open(file, "r") as lines:
        if skip_header:
            next(lines)
        with ThreadPoolExecutor(max_workers) as executor:
            executor.map(
                get_geoc_data_gmap_,
                lines,
                repeat(gmaps),
                repeat(region),
                repeat(language),
                repeat(inDelim),
            )


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
    for type in types:
        levels += [TYPE2LEVEL.get(type)]
    levels = list(set(filter(lambda x: x, levels)))
    level = min_geoent(levels)
    return level


def emulate_nomatch_gmaps(recid):
    out = get_empty_here_schema()
    out.update({"recId": recid, "seqNumber": 0, "matchLevel": "NOMATCH"})
    return out


def parse_response_gmaps(response, recid, out_format, iso_crossover):
    """Parse the high level Gmaps response (list of results). Can contain more than 1 results as
    well as 0."""

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
            out.update({"country": iso_crossover.get(out.get("country"))})
            # iso 2 to iso 3 (align gmaps (ISO2) on HERE (ISO3))
            out.update({"matchLevel": types2level_crossover(out["matchLevel"])})
            if not out.get("latitude"):
                # in case there were no coordinates in the result, it's a NOMATCH
                out = emulate_nomatch_gmaps(recid)
            flush_result(out, out_format)
    else:
        out = emulate_nomatch_gmaps(recid)
        flush_result(out, out_format)


@app.command()
def harmonize_geoc_data_gmaps(
    file: str, inDelim: str = "|", out_format: str = None, header: bool = True
):
    """Harmonize Gmaps response with HERE Geocoding API responses (csv)"""
    assert out_format in ["csv", "jsonl"]
    iso_crossover = get_isocrossover()

    if out_format == "csv" and header:
        csvwriter = csv.DictWriter(sys.stdout, GEOC_OUTCOLS)
        csvwriter.writeheader()

    with open(file, "r") as lines:
        for line in lines:
            line = clean_text(line, inDelim=f" {inDelim} ")
            # clean cases like "Jack A. Claes Pavilion | Elk Grove Park District" returned by Gmaps

            try:
                recid, response = line.split(inDelim)
                parse_response_gmaps(response, recid, out_format, iso_crossover)
            except ValueError:
                pass
                # occurs when there is still an inDelim in the result
                # (e.g. "long_name": "S2|02 Robert-Piloty-Geb\u00e4ude")


if __name__ == "__main__":
    app()
