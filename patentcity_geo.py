import csv
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor
from glob import glob
from itertools import repeat
from zipfile import ZipFile

import requests
import typer
from bs4 import BeautifulSoup

from patentcity_utils import clean_text, get_dt_human
from patentcity_utils import ok, not_ok

####################################################################################################
#                               Parse LOC using libpostal
# Libpostal https://github.com/openvenues/libpostal
# Docker libpostal https://github.com/johnlonganecker/libpostal-rest-docker
# REST api https://github.com/johnlonganecker/libpostal-rest
# Note:
# - if set up on GCP, you need to set up firewall rules to authorize access from the requesting
# machine
# - get external IP of GCP compute engine https://console.cloud.google.com/networking/addresses/list
# ?project=<your-project>
# Then, to build on BigQuery, use schema/xx_entpars_*.json
#
#                           Geocode LOC using HERE Batch geocoding API
# Guide: developer.here.com/documentation/batch-geocoder/dev_guide/topics/request-constructing.html
# API ref: https://developer.here.com/documentation/batch-geocoder/dev_guide/topics/endpoints.html
####################################################################################################

app = typer.Typer()

# compile

# HERE Geocoding API
GEOC_URL = "https://batch.geocoder.ls.hereapi.com/6.2/jobs"
GEOC_OUTCOLS = [
    "recId",
    "seqNumber",
    "seqLength",
    "latitude",
    "longitude",
    "locationLabel",
    "addressLines",
    "street",
    "houseNumber",
    "building",
    "subdistrict",
    "district",
    "city",
    "postalCode",
    "county",
    "state",
    "country",
    "relevance",
    "matchType",
    "matchCode",
    "matchLevel",
    "matchQualityStreet",
    "matchQualityHouseNumber",
    "matchQualityBuilding",
    "matchQualityDistrict",
    "matchQualityCity",
    "matchQualityPostalCode",
    "matchQualityCounty",
    "matchQualityState",
    "matchQualityCountry",
]


def get_parsed_loc(loc, endpoint, debug):
    """Request http://endpoint/parser with query loc"""
    data = json.dumps({"query": clean_text(loc)})
    response = requests.post(f"http://{endpoint}/parser", data=data)
    if debug and response.status_code != 200:
        typer.secho(
            f"{loc} failed with status code {response.status_code}", fg=typer.colors.RED
        )
    return json.loads(response.text)


def flatten_parsed_loc(parsed_loc):
    """Flatten the libpostal response"""
    out = {}
    for e in parsed_loc:
        out.update({e["label"]: e["value"]})
    return out


def parse_loc(line, endpoint, debug):
    """Return the line with parsed LOCs"""
    line = json.loads(line)
    locs = line.get("loc")
    if locs:
        locs_ = []
        for loc in locs:
            parsed_loc = get_parsed_loc(loc, endpoint, debug)
            parsed_loc = flatten_parsed_loc(parsed_loc)
            parsed_loc.update({"raw": loc})
            locs_ += [parsed_loc]
        line.update({"loc": locs_})
    typer.echo(json.dumps(line))


@app.command()
def get_parsed_loc(
    path: str, endpoint: str, max_workers: int = 10, debug: bool = False
):
    """Print json lines with parsed loc to stdout
    :param path: path to data file(s)
    :param endpoint: api endpoint (ip:port)
    :param max_workers: nb of concurrent threads
    """
    files = glob(path)
    for file in files:
        with open(file, "r") as fin:
            data = fin.read().split("\n")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            executor.map(parse_loc, data, repeat(endpoint), repeat(debug))


@app.command()
def post_geoc_data(
    data: str,
    api_key: str,
    outCols: str = None,
    inDelim: str = "|",
    outDelim: str = ",",
    locationattributes: str = "addressDetails",
    countryfocus: str = "gbr",
    language: str = "en-EN",
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
        log_msg = f"{data}\t{Status}\t{RequestId}\t{get_dt_human()}"
        if verbose:
            typer.echo(soup.prettify())
        if Status == "accepted":
            typer.secho(f"{ok}\t{log_msg}", fg=typer.colors.GREEN)
        else:
            typer.secho(f"{not_ok}\t{log_msg}", fg=typer.colors.RED)

    headers = {"Content-Type": "text/plain"}
    outCols = outCols.split(",") if outCols else GEOC_OUTCOLS

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
    )

    data = open(data, "rb").read()
    response = requests.post(GEOC_URL, headers=headers, params=params, data=data)
    if response.status_code == 200:
        check_post(response)
    else:
        typer.secho(
            f"{not_ok}Failed with status {response.status_code}\n{response.content}",
            fg=typer.colors.RED,
        )


@app.command()
def get_geoc_status(request_id: str, api_key: str, freq: int = 5, verbose=False):
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
def get_geoc_data(
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
    """Write material for batch geocoding using HERE API to stdout. Receive a jsonl file."""
    with open(file, "r") as lines:
        typer.echo(f"recId{inDelim}searchText")  # This is the required header
        for line in lines:  # iterate over file lines {"loc":[{""},{}],...}
            line = json.loads(line)
            locs = line.get("loc")
            if locs:  # if no loc found, no need to geocode it...
                for loc in locs:
                    typer.echo(f"{loc['uid']}{inDelim}{loc['raw']}")


def get_header(file, outDelim):
    with open(file, "r") as lines:
        for line in lines:
            header = line.replace("\n", "").split(outDelim)
            break
        return header


# @app.command()
def get_geoc_index(file: str, outDelim: str = ",", dump: bool = True):
    """Create index of here results {recId:{"latitude":"","longitude":"",...}}"""

    header = get_header(file, outDelim)
    index = {}
    with open(file, "r") as fin:
        csv_reader = csv.DictReader(fin, fieldnames=header)
        for i, line in enumerate(csv_reader):
            if i > 0:
                line = dict(line)
                if int(line["seqNumber"]) > 1:
                    # we keep only the first proposed item
                    # TODO evaluate policy
                    pass
                else:
                    recid = line["recId"]
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


@app.command(deprecated=True)
def here_to_jsonl(file: str):
    """Print lines of <file> as json object {"publication_number":"CC-DDDD-TT", "geoc": {...}}

    After that, group by publication_number using the following cli:
    jq -sc 'def array_agg($k): group_by(.[$k])[] | map(.geoc) as $geoc | .[0] | .geoc = $geoc ;
    array_agg("publication_number")' GB/result_*.jsonl >> geoc_*.jsonl
    stackoverflow.com/questions/48321235/sql-style-group-by-aggregate-functions-in-jq-count-sum
    -and-etc

    DEPRECATED in favor of get_geoc_index
    """

    header = get_header(file)
    with open(file, "r") as fin:
        csv_reader = csv.DictReader(fin, fieldnames=header)
        for i, line in enumerate(csv_reader):
            if i > 0:  # skip header
                line = dict(line)
                publication_number, _ = line["recId"].split("_")
                if int(line["seqNumber"]) > 1:
                    # we keep only the first proposed item
                    # TODO evaluate policy
                    pass
                else:
                    if line.get(
                        "SeqNumber"
                    ):  # causes conflict in BQ which is NOT case-sensitive
                        line.pop("SeqNumber")
                    typer.echo(
                        json.dumps(
                            {"publication_number": publication_number, "geoc": line}
                        )
                    )


@app.command()
def add_geoc_data(src, geoc_file: str = None, max_workers: int = 5):
    """Add geoc data from geoc_file returned by HERE batch geocoding API"""

    def update_loc(blob, index):
        blob = json.loads(blob)
        locs = []

        for loc_ in blob["loc"]:
            recid = loc_["recId"]
            geoc_ = index.get(recid)
            if geoc_:
                geoc_.pop("recId")  # avoid duplicates
                loc_.updat(geoc_)
            locs += [loc_]

        blob.update({"loc": locs})
        typer.echo(json.dumps(blob))

    index = get_geoc_index(geoc_file, dump=False)
    blobs = open(src, "r")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(update_loc, blobs, repeat(index))


if __name__ == "__main__":
    app()
