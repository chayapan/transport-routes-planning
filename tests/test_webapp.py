import requests
import json
import random
import pandas as pd
from maps_platform_api import Location, LocationTable
from maps_platform_api import Route, DistanceMatrix, print_location_table


def test_print_location_table():
    print_location_table()  # read CSV and dump HTML.


def test_getlatlng_from_location_address():
    f = "data/location_table.csv"
    columns = [
        "LocationID",
        "Province",
        "RowID",
        "Store No",
        "Store Name",
        "Store Type",
        "Address",
        "Remark1",
        "Remark2",
    ]
    df = pd.read_csv(f, index_col="LocationID", names=columns, header=0)
    for row in df.iterrows():
        store_no = row[1]["Store No"]
        store_name = row[1]["Store Name"]
        addr = row[1]["Address"]
        loc = Location.from_address(addr)
        lat, lng = loc.get_latlng()
        loc.name = store_name
        loc.id = store_no
        print(lat, lng, store_no, store_name, addr, loc)


def test_locationtable_obj():
    l = LocationTable()
    assert len(l._data) > 0, "initialized LocationTable instance from CSV"


def test_locationtable_to_geojson():
    l = LocationTable()
    geojson_data = l.to_geojson()
    dict_data = l.to_geojson(as_dict=True)
    # print(dict_data)
    # print(geojson_data)
    assert geojson_data.startswith("""{"type": "FeatureCollection", "features": ["""), (
        "GeoJSON not as expected: " + geojson_data
    )
    assert (
        len(dict_data["features"]) > 1 and dict_data["type"] == "FeatureCollection"
    ), "GeoJSON obj dict = " + str(dict_data)
    outfile = "webapp/locations.geojson"
    with open(outfile, "w") as f:
        f.write(geojson_data)
