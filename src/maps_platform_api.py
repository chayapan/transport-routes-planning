import requests
import json
import pandas as pd

API_KEY = "AIzaSyBTt6fQaix-5G7_1-c3aBt1EiJ2zp03kbw"


def get_geocode_result(address):
    """Return JSON object or None."""
    url = "https://maps.googleapis.com/maps/api/geocode/json?address={}&key={}".format(
        address, API_KEY
    )
    res = requests.get(url)
    assert res.status_code == 200
    result = json.loads(res.content)
    assert result["status"] == "OK", res.content
    return result


class Location:
    def __init__(self, json_data, id=None, name=None):
        """Wrapper for Google's geocode result. Optionally assign identifier."""
        self.id = id
        self.name = name
        self._json = json_data

    @property
    def formatted_address(self):
        """formatted_address return first of the result"""
        if not "results" in self._json:
            return ""
        return self._json["results"][0]["formatted_address"]

    def get_latlng(self):
        """results[0]
        "geometry": {
            "location": {
              "lat": 13.7520996,
              "lng": 100.5296451
            },
        """
        if not "results" in self._json:
            return None, None
        loc = self._json["results"][0]["geometry"]["location"]
        return loc["lat"], loc["lng"]

    @classmethod
    def from_address(cls, address):
        """ex. Location.from_address("1 Phayathai Road, Bangkok") => Location()"""
        result = get_geocode_result(address)
        return cls(result)

    def __repr__(self):
        return "<Location {}[{}] {} ({})/>".format(
            self.id, self.name, self.formatted_address, self.get_latlng()
        )


class Route:
    def __init__(self, a: Location = None, b: Location = None):
        """Representation of route from location A to location B.
        Use Route API per https://developers.google.com/maps/documentation/routes/compute_route_directions
        """
        self.origin = a
        self.destination = b
        self.duration = "0s"
        self.distanceMeters = "0"
        self.polyline = ""

    def get_route(self):
        # if origin is the same as destination return None.
        lat1, lng1 = self.origin.get_latlng()
        lat2, lng2 = self.destination.get_latlng()
        if lat1 == lat2 and lng1 == lng2:
            self.route_result = None
        else:
            result = self.call_()
            self.route_result = result
            self.duration = result["routes"][0]["duration"]
            self.distanceMeters = result["routes"][0]["distanceMeters"]
            self.polyline = result["routes"][0]["polyline"]

    def build_request(self):
        """Prepare the API call parameter.
                {
          "origin":{
            "location":{
              "latLng":{
                "latitude": 37.419734,
                "longitude": -122.0827784
              }
            }
          },
          "destination":{
            "location":{
              "latLng":{
                "latitude": 37.417670,
                "longitude": -122.079595
              }
            }
          },
          "travelMode": "DRIVE",
          "routingPreference": "TRAFFIC_AWARE",
          "computeAlternativeRoutes": false,
          "routeModifiers": {
            "avoidTolls": false,
            "avoidHighways": false,
            "avoidFerries": false
          },
          "languageCode": "en-US",
          "units": "IMPERIAL"
        }
        """
        url = "https://routes.googleapis.com/directions/v2:computeRoutes"

        header = {}
        header["Content-Type"] = "application/json"
        header["X-Goog-Api-Key"] = API_KEY
        header["X-Goog-FieldMask"] = (
            "routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline"
        )

        lat1, lng1 = self.origin.get_latlng()
        lat2, lng2 = self.destination.get_latlng()
        param = {}
        param["origin"] = {}
        param["origin"]["location"] = {}
        param["origin"]["location"]["latLng"] = {"latitude": lat1, "longitude": lng1}
        param["destination"] = {}
        param["destination"]["location"] = {}
        param["destination"]["location"]["latLng"] = {
            "latitude": lat2,
            "longitude": lng2,
        }
        param["travelMode"] = "DRIVE"
        param["routingPreference"] = "TRAFFIC_AWARE"
        param["computeAlternativeRoutes"] = False
        param["routeModifiers"] = {
            "avoidTolls": False,
            "avoidHighways": False,
            "avoidFerries": False,
        }
        param["languageCode"] = "en-US"
        param["units"] = "IMPERIAL"
        # assert False, (url, param, header)
        return url, param, header

    def call_(self):
        url, param, header = self.build_request()
        res = requests.post(url, data=json.dumps(param), headers=header)
        print(res.status_code)
        print(res.content)
        result = json.loads(res.content)
        return result

    def __repr__(self):
        return "<Route {} {} {} -> {} />".format(
            self.distanceMeters,
            self.duration,
            self.origin.get_latlng(),
            self.destination.get_latlng(),
        )


def print_location_table(f="data/location_table.csv"):
    """Read CSV and print table to HTML for webapp."""
    columns = [
        "LocationID",
        "Province",
        "RowID",
        "Store No",
        "Store Name",
        "Format Group",
        "Address",
        "Remark1",
        "Remark2",
    ]
    df = pd.read_csv(f, index_col="LocationID", names=columns, header=0)
    with open("webapp/location_table.html", "w") as f:
        f.write(df.to_html())
    return df


class LocationTable:
    def __init__(self, f="data/location_table.csv"):
        columns = [
            "LocationID",
            "Province",
            "RowID",
            "Store No",
            "Store Name",
            "Format Group",
            "Address",
            "Remark1",
            "Remark2",
        ]
        # load data and fetch lat/lng
        df = pd.read_csv(f, index_col="LocationID", names=columns, header=0)
        self._data = {}
        for row in df.iterrows():
            store_no = row[1]["Store No"]
            store_name = row[1]["Store Name"]
            addr = row[1]["Address"]
            loc = Location.from_address(addr)
            lat, lng = loc.get_latlng()
            loc.name = store_name
            loc.id = store_no
            # print(lat, lng, store_no, store_name, addr, loc)
            self._data[store_no] = loc


class DistanceMatrix:
    def __init__(self):
        """
        Constructor:
        # the matrix
        #  (origin,destination) => route
                    matrix[(name1, name2)] = (id1, id2, r)
        """
        self._m = {}
        self.rows = []

    @property
    def locations(self):
        """Location is the row items. This stores location ID."""
        loc = []
        for location in self.rows:
            if not location in loc:
                loc.append(location)
        return loc

    def add_path(self, from_loc: Location, to_loc: Location, route: Route = None):
        if not route:
            route = Route(from_loc, to_loc)
        k = (from_loc.id, to_loc.id)
        self._m[k] = (from_loc, to_loc, route)  # locA, locB, routeAB
        if from_loc.id not in self.rows:
            self.rows.append(from_loc.id)

    def print_matrix(self):
        headers = "  " + " ".join(map(str, self.locations))
        rows = "\n"
        for r in self.locations:
            rows += "{}".format(r)
            for i in self.locations:
                if (i, r) in self._m.keys():
                    e = "d{}{} ".format(i, r)
                else:
                    e = ""
            rows += e + "\n"
        print(headers + rows)
        return True

    def to_dataframe(self):
        # TODO...
        rows = []
        for k, v in self._m.items():
            # (id1, id2) => (name1, name2, route)
            row = {"from": v[0], "to": v[1], "distance": v[2]}
            rows.append(row)
        return pd.DataFrame(rows)
