"""Lib of var used in patencity CLI"""
import json
import os

ROOT_DIR = os.path.dirname(os.path.abspath("setup.py"))
ISO_FILE = os.path.join(ROOT_DIR, "lib/iso_crossover.json")

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
HERE2GMAPS = {
    "recId": "recId",
    "seqNumber": "seqNumber",
    "seqLength": "",
    "latitude": "lat",
    "longitude": "lng",
    "locationLabel": "formatted_address",
    "addressLines": "",
    "street": "route_long_name",
    "houseNumber": "street_number_long_name",
    "building": "premise_long_name",
    "subdistrict": "",
    "district": "sublocality_long_name",
    "city": "locality_long_name",
    "postalCode": "postal_code_long_name",
    "county": "administrative_area_level_2_long_name",
    "state": "administrative_area_level_1_long_name",
    "country": "country_short_name",
    "relevance": "",
    "matchType": "location_type",
    "matchCode": "",
    "matchLevel": "",
    "matchQualityStreet": "",
    "matchQualityHouseNumber": "",
    "matchQualityBuilding": "",
    "matchQualityDistrict": "",
    "matchQualityCity": "",
    "matchQualityPostalCode": "",
    "matchQualityCounty": "",
    "matchQualityState": "",
    "matchQualityCountry": "",
}


# https://developers.google.com/maps/documentation/geocoding/overview


def get_isocrossover(file: str = None, reverse: str = False):
    """Return a dict of iso crossover"""
    if not file:
        file = ISO_FILE
    out = json.loads(open(file, "r").read())
    if reverse:
        out = {v: k for k, v in out.items()}
    return out


def list_countrycodes(file: str = None):
    """Return a list of country codes (iso 2 and 3)"""
    if not file:
        file = ISO_FILE
    countrycodes = json.loads(open(file, "r").read())
    return list(countrycodes.keys()) + list(countrycodes.values()) + ["BRD"]
