"""Client 2: retrieve stored sensor measurements using HTTP GET."""

import argparse
import sys

import requests

API_URL = "http://127.0.0.1:5000/api/light"


def main():
    parser = argparse.ArgumentParser(description="Retrieve sensor data via HTTP GET")
    parser.add_argument("--area", type=int, default=None, help="Area to query (default: None)")
    args = parser.parse_args()

    try:
        response = requests.get(API_URL, params={"area": args.area}, timeout=5)
        print("[Client 2] GET:", response.url)
        print("[Server] HTTP status:", response.status_code)
        if not response.ok:
            print("[Server] Error:", response.text)
            return 1

        data = response.json()
        print("[Server] Number of records:", data["count"])
        for item in data["data"]:
            print("  {timestamp} | area={area} | lux={lux}".format(**item))
    except (requests.exceptions.RequestException, ValueError, KeyError) as exc:
        print("[Error] Could not retrieve sensor data:", exc, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
