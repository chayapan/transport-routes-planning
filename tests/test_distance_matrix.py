import requests
import json
import random
from maps_platform_api import Location, API_KEY, get_geocode_result
from maps_platform_api import Route, DistanceMatrix


def write_json_output(json_data, filename):
    with open(filename, "w") as f:
        f.write(json.dumps(json_data, indent=2))


def mock_location_table(count=10):
    locname = "Location%03d"
    locations = {}
    get_soi = lambda: random.choice(["", "", "Soi %s" % random.randint(1, count)])
    get_road = lambda: random.choice(
        ["Payathai", "Ramkamhang", "Sukhumvit", "Rama 4", "Phetkasem"]
    )
    for i in range(1, count + 1):
        locations[i] = (i, locname % i, "%s %s %s Bangkok" % (i, get_soi(), get_road()))
    return locations


def test_save_datafile():
    locations = mock_location_table(count=10)
    write_json_output(locations, "data/locations.json")
    assert len(locations) == 10


def test_load_datafile():
    with open("data/locations.json") as f:
        data = json.loads(f.read())
    assert len(data) == 10


def test_generate_mock_location_table():
    locations = mock_location_table()
    with open("output/locations.json", "w") as f:
        f.write(json.dumps(locations, indent=2))
    assert len(locations) > 0, locations


def test_call_api():
    """get location from address"""
    address = "1 phayathai bangkok"
    url = "https://maps.googleapis.com/maps/api/geocode/json?address={}&key={}".format(
        address, API_KEY
    )
    res = requests.get(url)
    assert res.status_code == 200
    result = json.loads(res.content)
    assert result["status"] == "OK"
    write_json_output(result, "output/address_1.json")


def test_get_two_locations():
    address1 = "1 phayathai bangkok"
    address2 = "99 phayathai bangkok"
    result1 = get_geocode_result(address1)
    result2 = get_geocode_result(address2)
    write_json_output(result1, "output/loc01.json")
    write_json_output(result2, "output/loc02.json")
    print(Location(result1))
    print(Location(result2))


def test_get_latlng():
    address1 = "1 phayathai bangkok"
    result1 = get_geocode_result(address1)
    loc1 = Location(result1)
    print(loc1.formatted_address)
    print(loc1.get_latlng())
    assert loc1.get_latlng(), "Get Lat,Lng. {}".format(loc1)


def test_get_a_route_between_two_locations():
    address1 = "1 phayathai bangkok"
    address2 = "99 phayathai bangkok"
    result1 = get_geocode_result(address1)
    result2 = get_geocode_result(address2)
    location1 = Location(result1)
    location2 = Location(result2)
    route = Route(location1, location2)
    route.get_route()
    assert route.route_result, route.route_result
    assert isinstance(route, Route), route


def test_make_distance_matrix_from_location_table():
    N = 5  # 5,30,50,500
    locations = mock_location_table(count=N)
    dist_m = DistanceMatrix()
    matrix = {}
    for k1, v1 in locations.items():
        id1, name1, address1 = v1
        for k2, v2 in locations.items():
            id2, name2, address2 = v2
            # dont compute route on same location
            pair = (k1, k2)
            if id1 != id2 and address1 != address2:
                result1 = get_geocode_result(address1)
                result2 = get_geocode_result(address2)
                a = Location(result1, id=id1, name=name1)
                b = Location(result2, id=id2, name=name2)
                r = Route(a, b)
                r.get_route()
                with open("output/%s_%s.txt" % (id1, id2), "w") as f:
                    f.write(str(r))
                matrix[(id1, id2)] = (name1, name2, r)
                dist_m.add_path(a, b, r)
    # the matrix
    #  (origin,destination) => route
    assert len(matrix) > 1, matrix
    # write_json_output(matrix, "output/matrix.json")  # error cannot dump tuple
    df = dist_m.to_dataframe()
    df.set_index("") ****
    df.to_csv("output/dist_m.csv")
