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
        return self._json["results"][0]["formatted_address"]

    def get_latlng(self):
        """results[0]
        "geometry": {
            "location": {
              "lat": 13.7520996,
              "lng": 100.5296451
            },
        """
        loc = self._json["results"][0]["geometry"]["location"]
        return loc["lat"], loc["lng"]

    @classmethod
    def from_address(cls, address):
        """ex. Location.from_address("1 Phayathai Road, Bangkok") => Location()"""
        result = get_geocode_result(address)
        return cls(result)

    def __repr__(self):
        return "<Location {} ({})/>".format(self.formatted_address, self.get_latlng())


class Route:
    def __init__(self, a: Location, b: Location):
        """Representation of route from location A to location B.
        Use Route API per https://developers.google.com/maps/documentation/routes/compute_route_directions
        """
        self.origin = a
        self.destination = b
        # if origin is the same as destination return None.
        lat1, lng1 = self.origin.get_latlng()
        lat2, lng2 = self.destination.get_latlng()
        if lat1 == lat2 and lng1 == lng2:
            self.route_result = None
            self.duration = "0s"
            self.distanceMeters = "0"
            self.polyline = ""
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


class DistanceMatrix:
    def __init__(self):
        """
        Constructor:
        # the matrix
        #  (origin,destination) => route
                    matrix[(name1, name2)] = (id1, id2, r)
        """
        self._m = {}
        self.cols = []
        self.rows = []

    def add_path(self, from_loc: Location, to_loc: Location, route: Route = None):
        if not route:
            route = Route(from_loc, to_loc)
        k = (from_loc.id, to_loc.id)
        self._m[k] = (from_loc.name, to_loc.name, route)
        if not from_loc in self.rows:
            self.rows.append(from_loc)
        if not to_loc in self.cols:
            self.cols.append(to_loc)

    def to_dataframe(self):
        # TODO...
        rows = []
        for k, v in self._m.items():
            # (id1, id2) => (name1, name2, route)
            row = {"from": v[0], "to": v[1], "distance": v[2]}
            rows.append(row)
        return pd.DataFrame(rows)
