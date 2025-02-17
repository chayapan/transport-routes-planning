import argparse
from maps_platform_api import DistanceMatrix, Location, json

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(
    dest="command", required=True, help="Available subcommands"
)
list_parser = subparsers.add_parser("locations", help="List locations")
list_parser.add_argument("--files", help="Input files")
run_parser = subparsers.add_parser("run", help="Do execute get route")
run_parser.add_argument("--files", help="Input files")
args = parser.parse_args()


def get_location_table(filename):
    with open(filename, "r") as f:
        data = json.loads(f.read())
    return data


def make_distance_matrix(locations: dict):
    """Make distance matrix from location dictionary."""
    m = DistanceMatrix()
    for k1, v1 in locations.items():
        id1, name1, address1 = v1
        for k2, v2 in locations.items():
            id2, name2, address2 = v2
            # dont compute route on same location
            if id1 != id2 and name1 != name2:
                m.add_path(
                    Location(json_data={}, id=id1, name=name1),
                    Location(json_data={}, id=id2, name=name2),
                    {},
                )
    return m


def run():
    print("Run...")
    # worker


def main():
    if args.files:
        print("Reading from {}".format(args.files))
    locations = get_location_table(args.files)
    d = make_distance_matrix(locations)
    print("Locations: {}".format(len(d.locations)))
    print(locations)
    print("=" * 80)
    print(d.locations)
    print("Paths/Edges: {}".format(len(d._m)))
    d.print_matrix()


if __name__ == "__main__":
    print(args.command)
    if args.command == "locations":
        main()
    if args.command == "run":
        run()
