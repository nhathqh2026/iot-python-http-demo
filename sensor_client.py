"""Client 1: simulate an IoT light sensor by sending HTTP POST."""

import argparse
import sys
from datetime import datetime

import requests

LIGHT_API_URL = "http://127.0.0.1:5000/api/light"


def main():
    parser = argparse.ArgumentParser(description="Send a sensor measurement via HTTP POST")
    parser.add_argument("--area", type=int, default=1, help="Sensor area (default: 1)")
    parser.add_argument("--lux", type=float, default=500, help="Light value in lux (default: 500)")
    args = parser.parse_args()

    # Generate the measurement timestamp on the sensor side (local clock, seconds).
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lux = int(args.lux) if args.lux.is_integer() else args.lux
    data = {"timestamp": timestamp, "area": args.area, "lux": lux}
    print("[Client 1] Sending POST to:", LIGHT_API_URL)
    print("[Client 1] JSON:", data)

    try:
        response = requests.post(LIGHT_API_URL, json=data, timeout=5)
        print("[Server] HTTP status:", response.status_code)
        print("[Server] Response:", response.text)
        print("[Server] Response OK:", response.ok)
        if not response.ok:
            return 1
    except requests.exceptions.RequestException as exc:
        print("[Error] Cannot contact HTTP Server:", exc, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

