"""Lib of var used in patencity CLI"""
import json

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


def get_isocrossover(file: str = "lib/iso_crossover.json", reverse: str = False):
    """Return a dict """
    out = json.loads(open(file, "r").read())
    if reverse:
        out = {v: k for k, v in out.items()}
    return out
