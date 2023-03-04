"""
General purpose utilities
"""
import csv
import datetime
import json
import os
import re
import string
import sys
from concurrent.futures import ThreadPoolExecutor
from glob import glob
from hashlib import md5
from itertools import repeat
from operator import itemgetter
from pathlib import Path

import numpy as np
import pandas as pd
import spacy
import typer
import yaml

# from fuzzyset import FuzzySet
from fuzzysearch import find_near_matches
from smart_open import open  # pylint: disable=redefined-builtin
from spacy.tokens import DocBin
from spacy.training import Example

from patentcity.lib import GEOC_OUTCOLS, get_isocrossover, list_countrycodes

# msg utils
ok = "\u2713"
not_ok = "\u2717"

app = typer.Typer()
TAG_RE = re.compile(r"<[^>]+>")
WHITE_RE = re.compile(r"\s+")

levels = [
    "country",
    "state",
    "county",
    "city",
    "postalCode",
    "district",
    "street",
    "houseNumber",
]


def clean_text(text, inDelim=None):
    """Remove anchors <*> and </*> and replace by an empty space"""
    if isinstance(text, str):
        text = TAG_RE.sub(" ", text)
        text = WHITE_RE.sub(" ", text)
        text = text.replace("\n", " ")
        if inDelim:
            text = text.replace(inDelim, " ")
    return text


def get_dt_human():
    """Return current datetime for human (e.g. 23/07/2020 11:30:59)"""
    return datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def get_recid(s, toint: bool = False):
    """Return the a uid made of the publication number and a random sequence 2^n random
    characters"""

    recid = md5(s.encode()).hexdigest()
    if toint:
        recid = int(recid, 16)
    return recid


def get_group(pubnum: int, u_bounds: str):
    u_bounds = [int(u_bound) for u_bound in u_bounds.split(",")]
    try:
        group = int(max(np.where(np.array(u_bounds) <= pubnum)[0]) + 2)
    except (
        ValueError
    ):  # case where the pubnum is lower than any bound, hence in group 1
        group = 1
    return group


def get_pubnum(fname: str):
    try:
        pubnum = int(fname.split("-")[1])
    except (ValueError, IndexError):
        pubnum = None
        typer.secho(f"{not_ok}{fname} Publication number ill-formatted.")
    return pubnum


def get_empty_here_schema():
    return {k: None for k in GEOC_OUTCOLS}


def flatten(l):
    return [item for sublist in l for item in sublist]


def move_file(file, u_bounds):
    fname = os.path.basename(file)
    if fname:
        pubnum = get_pubnum(fname)
        if pubnum:
            group = get_group(pubnum, u_bounds)
            dest = os.path.join(os.path.dirname(file), f"group_{group}", fname)
            os.rename(file, dest)
            typer.secho(f"{ok}Move {file}->group_{group}/", fg=typer.colors.GREEN)


def read_csv_many(path: str, verbose=False, **kwargs):
    """Append tables defined by files in `path` ()"""
    files = glob(path)
    for i, file in enumerate(files):
        tmp_ = pd.read_csv(file, **kwargs)
        if verbose:
            typer.secho(f"Using {file}", color=typer.colors.BLUE)
        # breakpoint()
        if i == 0:
            tmp = tmp_.copy()
        else:
            tmp = tmp.append(tmp_)  # , error_bad_lines=False
    return tmp


@app.command()
def make_groups(path: str, u_bounds: str = None, max_workers: int = 10):
    """Distribute files in folders by groups. u_bounds (upper bounds of the groups) should be
    ascending & comma-separated."""
    files = glob(path)
    for i in range(len(u_bounds.split(",")) + 1):
        os.mkdir(os.path.join(os.path.dirname(path), f"group_{i + 1}"))

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(move_file, files, repeat(u_bounds))


@app.command()
def prep_annotation_groups(path: str, u_bounds: str = None):
    """Print files as proper prodigy jsonl input. Include with a 'format' field indicating the
    format the document belongs to."""

    files = glob(path)
    for file in files:  # could be multi threaded but not worth it
        fname = os.path.basename(file)
        # path = os.path.join(dir, fname)
        if fname:
            pubnum = get_pubnum(fname)
            publication_number = fname.replace(".txt", "")
            group = get_group(pubnum, u_bounds)
            with open(file, "r") as fin:
                out = {
                    "text": fin.read(),
                    "publication_number": publication_number,
                    "group": group,
                }
                typer.echo(json.dumps(out))


@app.command()
def get_buggy_labels(file: str):
    """Print info on labels with leading/trailing space.
    Expect a jsonl file with lines following a simple annotation model"""
    with open(file, "r") as lines:
        for i, line in enumerate(lines):
            line = json.loads(line)
            text = line["text"]
            spans = line.get("spans")
            punctuation_ = (
                string.punctuation.replace(".", "").replace("(", "").replace(")", "")
            )
            if spans:
                for span in spans:
                    span_text = text[span["start"] : span["end"]]
                    startswith_space = any(
                        [span_text.startswith(" "), span_text.startswith(r"\s")]
                    )
                    endswith_space = any(
                        [span_text.endswith(r"\s"), span_text.endswith(" ")]
                    )
                    startswith_punctuation, endswith_punctuation = ([], [])
                    for punctuation in punctuation_:
                        startswith_punctuation += [span_text.startswith(punctuation)]
                        endswith_punctuation += [span_text.endswith(punctuation)]
                    startswith_punctuation = any(startswith_punctuation)
                    endswith_punctuation = any(endswith_punctuation)
                    if any(
                        [
                            startswith_space,
                            endswith_space,
                            startswith_punctuation,
                            endswith_punctuation,
                        ]
                    ):
                        typer.secho(f"{json.dumps(line)}", fg=typer.colors.YELLOW)
                        typer.secho(
                            f"Span:{span}\nValue:{span_text}\nLine:{i + 1}",
                            fg=typer.colors.RED,
                        )


@app.command()
def expand_pubdate_imputation(file: str, output: str = None):
    """Expand a sparse publication_date imputation file (with upper bound pubnum only) to a
    continuous (wrt pubnum) file."""
    df = pd.read_csv(file)
    max_pubnum = df.max()["pubnum"]
    expansion = pd.DataFrame(range(1, max_pubnum + 1), columns=["pubnum"])
    df_expansion = df.merge(expansion, how="right", left_on="pubnum", right_on="pubnum")
    df_expansion = df_expansion.fillna(method="backfill")
    for v in df_expansion.columns:
        df_expansion[v] = df_expansion[v].astype(int)
    df_expansion.to_csv(output, index=False)
    typer.secho(
        f"{ok} Imputation file expanded and saved in {output}", fg=typer.colors.GREEN
    )


@app.command()
def get_recid_nomatch(file, index, inDelim: str = "|"):
    """Retrieve the search text from recId which were not matched

    FILE is the HERE batch geocoding API output
    INDEX is the corresponding HERE batch geocoding API input
    """

    def get_search_text_index(index, inDelim):
        search_text_index = {}
        with open(index, "r") as lines:
            for line in lines:
                recid, searchtext = line.split(inDelim)
                searchtext = searchtext.replace("\n", "")
                search_text_index.update({recid: searchtext})
        return search_text_index

    search_text_index = get_search_text_index(index, inDelim)

    with open(file, "r") as lines:
        for line in lines:
            if "NOMATCH" in line:
                recid = line.split(",")[0]
                search_text = search_text_index.get(recid)
                typer.secho(f"{recid}{inDelim}{search_text}")
            else:
                pass


@app.command()
def prep_searchtext(file, config_file: str):
    """Prepare search text so as to avoid common pitfalls (country codes, postcodes, etc)"""
    with open(config_file, "r") as config_file_:
        config = yaml.load(config_file_, Loader=yaml.FullLoader)

    remove_postcode = config["postcode"]["remove"]
    remove_countrycode = config["countrycode"]["remove"]
    if remove_countrycode:
        countrycodes = config["countrycode"]["list"]
        countrycodes = (
            list_countrycodes()
            if countrycodes == "*"
            else config["countrycode"]["list"].split(",")
        )
    inDelim = config["inDelim"]

    with open(file, "r") as lines:
        for line in lines:
            line = line.replace("\n", "")
            recid, searchtext = line.split(inDelim)

            if remove_postcode:
                like_postcode = re.findall(r"\b\d{4,}\b", searchtext)
                if like_postcode:
                    for match in like_postcode:
                        searchtext = searchtext.replace(match, "")

            if remove_countrycode:
                like_countrycode = re.findall(
                    r"|".join(map(lambda x: r"(\b" + x + r")\b", countrycodes)),
                    searchtext,
                )
                if like_countrycode and len(searchtext) > 5:
                    like_countrycode = list(
                        filter(lambda x: x, sum(like_countrycode, ()))
                    )

                    for match in like_countrycode:
                        searchtext = searchtext.replace(match, "")
            typer.echo(f"{recid}{inDelim}{searchtext}")


def mcq(line, fset, ignore):
    line = json.loads(line)  # .replace("\n", "").split(indelim)
    if not line["recId"] in ignore:
        text = line["text"]
        closests = fset.get(text)
        if closests:
            closests = [closest[1] for closest in closests]
            line.update(
                {
                    "options": [
                        {"id": closest, "text": closest} for closest in closests
                    ],
                    "accept": [closests[0]],
                }
            )
            typer.echo(json.dumps(line))
        else:
            pass
    else:
        pass


# TODO - fix fuzzyset installation issue and restore or remove
# @app.command()
# def mcq_factory(
#     loc: str = None, index: str = None, max_workers: int = 5, list_ignore: str = None
# ):
#     """Return jsonl for choice prodigy view-id based on fuzzyset suggestion for each line based
#     on the text of each line in the loc file and the targets in the index file"""
#     targets = open(index, "r").read().split("\n")
#     fset = FuzzySet()
#     for target in targets:
#         fset.add(target)
#     if list_ignore:
#         with open(list_ignore, "r") as ignore:
#             ignore = ignore.read().replace('"', "").split("\n")
#     else:
#         ignore = []
#     with open(loc, "r") as lines:
#         with ThreadPoolExecutor(max_workers=max_workers) as executor:
#             executor.map(mcq, lines, repeat(fset), repeat(ignore))


@app.command()
def mcq_revert(file, max_options: int = 50):
    """Revert a sequence of mcq where main text is the raw text and options are
    targets into a sequence of mcq where the target is the main text and options are the raw text
    """

    def revert_line(line, index):
        for option in line.get("options"):
            text = option["id"]
            if not index.get(text):
                index.update({text: []})
            text_options = index[text] + [
                {
                    "id": line["recId"],
                    "text": line["text"],
                    "nb_occurences": line["nb_occurences"],
                    "eg_publication_number": line["eg_publication_number"],
                }
            ]
            index.update({text: text_options})
            return index

    index = {}
    with open(file, "r") as lines:
        for line in lines:
            line = json.loads(line)
            index = revert_line(line, index)

    tasks = []
    for text, options in index.items():
        options = sorted(options, key=itemgetter("nb_occurences"), reverse=True)
        # if len(options) > max_options:
        for chunk_options in [
            options[x : x + max_options] for x in range(0, len(options), max_options)
        ]:
            tasks += [
                {
                    "text": text,
                    "nb_occurences": max(opt["nb_occurences"] for opt in chunk_options),
                    "options": chunk_options,
                }
            ]
    tasks = sorted(tasks, key=itemgetter("nb_occurences"), reverse=True)
    for task in tasks:
        typer.echo(json.dumps(task))


@app.command()
def prep_disamb_index(file: str, inDelim: str = "|"):
    """Return a list of recId(line)|line from a list of lines
    Should be used to prepare a list of disambiguation targets for downstream process (e.g.
    add-geoc-disamb"""
    with open(file, "r") as lines:
        for line in lines:
            line = clean_text(line, inDelim)
            recid = get_recid(line)
            typer.echo(f"{recid}{inDelim}{line}")


@app.command()
def prep_disamb(file: str, orient: str = "revert", inDelim: str = "|"):
    """Prep disamb file from mcq output data"""
    assert orient in ["revert"]
    with open(file, "r") as lines:
        for line in lines:
            line = json.loads(line)
            accepts = line.get("accept")
            text = line.get("text")
            for accept in accepts:
                typer.echo(f"{accept}{inDelim}{text}")


@app.command()
def disamb_countrycodes(file, inDelim: str = "|", verbose: bool = False):
    """Ingest a loc file with raw search text (recid|searchtext), match them against the list of iso2 and is3 codes and
    return lines with non null match recid|disamb(searchtext)"""
    countrycodes = list_countrycodes()
    with open(file, "r") as lines:
        for line in lines:
            recid, searchtext = line.split(inDelim)
            if len(searchtext) <= 5:
                like_countrycode = re.findall(
                    r"|".join(map(lambda x: r"(\b" + x + r")\b", countrycodes)),
                    searchtext,
                )
                matches = list(filter(lambda x: x, sum(like_countrycode, ())))
                if matches:
                    if verbose:
                        typer.echo(f"{recid}{inDelim}{searchtext}->{matches[0]}")
                    else:
                        typer.echo(f"{recid}{inDelim}{matches[0]}")


@app.command()
def generate_iso_override():
    """Generate the iso override file"""
    csvwriter = csv.DictWriter(sys.stdout, GEOC_OUTCOLS)
    countrycodes = list_countrycodes()
    iso_crossover = get_isocrossover()
    csvwriter.writeheader()
    for countrycode in countrycodes:
        out = get_empty_here_schema()
        country = countrycode if len(countrycode) == 3 else iso_crossover[countrycode]
        out.update(
            {
                "recId": get_recid(countrycode),
                "seqNumber": 1,
                "country": country,
                "matchLevel": "country",
            }
        )
        csvwriter.writerow(out)


@app.command()
def get_gmaps_index_wgp(
    file: str, flavor: int = None, inDelim: str = "|", verbose: bool = False
):
    """
    Return the csv file as the gmaps geoc index we are using in patentcity
    recId|{gmaps output}
    Next, it should be harmonized with HERE data.
    E.g. addresses_florian25.csv
    """
    assert flavor in [25, 45]
    recid_idx = 0 if flavor == 45 else -1
    with open(file, "r") as fin:
        csv_reader = csv.reader(fin, delimiter=",", escapechar="\\")
        for line in csv_reader:
            try:
                typer.echo(
                    f"{line[recid_idx]}{inDelim}{json.dumps(json.loads(line[3])['results'])}"
                )
            except Exception as e:  # pylint: disable=broad-exception-caught
                if verbose:
                    typer.secho(str(e), fg=typer.colors.RED)
            # the first field is the location id (eq recid)
            # the second field is the gmaps result


def get_cit_code(text: str, fst: dict, fuzzy_match: bool):
    """Return the ISO-3 country code of the detected citizenship

    If fuzzy match True, fuzzy match considered iff exact match None
    """

    def get_candidates(text: str, fst: dict, fuzzy_match: bool = True):
        # we start by considering only exact matches here
        text = text.lower()
        candidates = [key for key in fst.keys() if key.lower() in text.lower()]
        if not candidates and fuzzy_match:
            text = text.replace("laws", "")  # creates confusion with Laos
            candidates = [
                key
                for key in fst.keys()
                if find_near_matches(key.lower(), text.lower(), max_l_dist=1)
            ]
        return candidates

    def get_pred(candidates: list, fst: dict):
        candidates = [fst[candidate] for candidate in candidates]
        if len(set(candidates)) == 1:
            pred = candidates[0]
        elif len(candidates) > 1:
            # in case there are more than 1 candidates, we take the most frequent
            if "USA" in candidates and "JEY" in candidates:
                pred = "USA"
            elif "USA" in candidates and "NIU" in candidates:
                pred = "USA"
            elif "USA" in candidates and "IND" in candidates:
                pred = "USA"
            elif "DDR" in candidates and "DEU" in candidates:
                pred = "DDR"
            else:
                pred = max(candidates, key=candidates.count)
            # will randomly pick one if multi-max
        else:
            pred = None

        return pred

    candidates = get_candidates(text, fst, fuzzy_match)
    pred = get_pred(candidates, fst)

    return pred


class ReportFormat:
    def __init__(
        self,
        file: Path,
        bins: iter,
        lang: str = None,
        crop: bool = True,
        md: bool = False,
    ):
        self.file = file
        self.bins = bins
        self.lang = lang
        self.crop = crop
        self.md = md
        self.nlp = spacy.blank(self.lang) if self.lang else self.lang
        self.unit = "tok" if self.lang else "char"

    def hist_to_stdout(self, a):
        hist_vals, hist_bins = np.histogram(a, bins=self.bins)
        if self.crop:
            nonzero = np.where(hist_vals != 0)
            hist_vals, hist_bins = hist_vals[nonzero], hist_bins[nonzero]

        if self.md:
            typer.echo("```shell script")
        for i in range(len(hist_vals)):
            typer.echo(
                f"{hist_bins[i]}\t" + "+" * (hist_vals / len(a) * 100).astype(int)[i]
            )
        if self.md:
            typer.echo("```")

    def get_data(self):
        # typer.echo("Acquiring data ...")
        with self.file.open("r") as lines:
            lengths = []
            span_starts = []
            for line in lines:
                line = json.loads(line)
                text = line["text"]
                spans = line.get("spans")
                if self.unit == "tok":
                    span_starts += [span["token_start"] for span in spans]
                else:
                    span_starts += [span["start"] for span in spans]

                if self.unit == "tok":
                    doc = self.nlp(text)
                    lengths += [len(doc)]
                else:
                    lengths += [len(text)]
            return lengths, span_starts

    def get_report(self):
        lengths, span_starts = self.get_data()
        typer.secho(f"# REPORT `{os.path.basename(self.file)}`", fg=typer.colors.BLUE)
        typer.secho(f"\n> ℹ️ Unit: {self.unit}\n", fg=typer.colors.BLUE)
        typer.secho("\n## Doc lengths\n", fg=typer.colors.BLUE)
        self.hist_to_stdout(lengths)
        typer.secho("\n## Span starts\n", fg=typer.colors.BLUE)
        self.hist_to_stdout(span_starts)


@app.command()
def report_format(
    path: str,
    bins: str = "0,2000,50",
    lang: str = None,
    crop: bool = True,
    md: bool = True,
):
    """
    Return the histogram of doc length and start span
    """
    files = list(Path().glob(path))
    start, end, by = list(map(int, bins.split(",")))
    bins = np.arange(start, end, by)
    for file in files:
        report = ReportFormat(file, bins=bins, lang=lang, crop=crop, md=md)
        report.get_report()


@app.command()
def prep_geoc_gold(gold: str, data: str):
    """Return a csv file with gold annotations"""

    def level2array(x):
        idx = levels.index(x) if x and str(x) != "nan" else None
        if idx:
            truth_array = [1] * (idx + 1) + [0] * (len(levels) - (idx + 1))
        else:
            truth_array = [0] * len(levels)
        return truth_array

    gold_df = pd.read_json(gold, lines=True)
    data_df = pd.read_json(data, lines=True)

    gold_ = gold_df.query("answer=='accept'")[["loc_text", "accept", "options"]]
    gold_["accept"] = gold_["accept"].apply(lambda x: x[0] if x else None)
    gold_["option"] = gold_["options"].apply(lambda x: x[-1]["id"] if x else None)

    out = data_df.merge(gold_, on="loc_text", how="left")
    truth_values = pd.DataFrame(
        data=out["accept"].apply(level2array).values.tolist(),
        columns=list(map(lambda x: x + "_is_true", levels)),
    )
    option_values = pd.DataFrame(
        data=out["option"].apply(level2array).values.tolist(),
        columns=list(map(lambda x: x + "_is_option", levels)),
    )

    out = out.merge(truth_values, right_index=True, left_index=True).merge(
        option_values, right_index=True, left_index=True
    )

    typer.echo(out.to_csv())


@app.command()
def is_pers_to_spacy(file: Path, dest: Path, language: str):
    """
    Return a proper spaCy v3 training file for a `textcat` pipeline. Ingest a jsonl file generated by `prodigy db-out`.

    Arguments:
        file: `prodigy db-out` file path (jsonl)
        dest: destination file path (.spacy)
        language:

    **Usage:**
        ```shell
        patentcity utils is-pers-to-spacy data/train_ispers_xxpatentxx.jsonl data/train_ispers_xxpatentxx.spacy xx
        ```

    !!! note "restricted support"
        Only support IS_PERS but could be easily extended
    """
    CATS = {"PERS": 0, "NOT_PERS": 0}
    egs = []
    nlp = spacy.blank(language)
    doc_bin = DocBin()
    with file.open("r") as lines:
        for line in lines:
            line = json.loads(line)
            cats = CATS.copy()
            text = line["text"]
            doc = nlp(text)
            answer = line["answer"]
            if answer == "accept":
                cats.update({"PERS": 1})
            else:
                cats.update({"NOT_PERS": 1})
            if answer != "ignore":
                egs += [Example.from_dict(doc, {"cats": cats})]
    for eg in egs:
        doc_bin.add(eg.reference)
    doc_bin.to_disk(dest)


@app.command()
def print_schema(schema: str) -> None:
    """
    Print the json `schema` as a markdown table.

    Arguments:
        schema: json schema file

    **Usage:**
        ```shell
        patentcity utils print-schema schema/patentcity_v1.json
        ```
    """
    df = pd.read_json(schema)
    nested = df.query("fields==fields")
    unnested = pd.DataFrame()
    for i in range(len(nested)):
        tmp = pd.DataFrame.from_dict(nested["fields"].values[i])
        tmp["name"] = tmp["name"].apply(
            lambda x: ".".join(
                [nested["name"].values[i], x]  # pylint: disable=cell-var-from-loop
            )
        )
        unnested = unnested.append(tmp)

    out = (
        df.query("fields!=fields")
        .append(unnested)
        .drop("fields", axis=1)[["name", "description", "mode", "type"]]
    )
    typer.echo(out.to_markdown(index=False))


if __name__ == "__main__":
    app()
