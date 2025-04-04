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
    lt = LocationTable()
    assert len(lt._data) > 0, "initialized LocationTable instance from CSV"
