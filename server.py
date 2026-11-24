"""Simple HTTP server for the IoT teaching demo (local use only)."""

import csv
import math
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request

app = Flask(__name__)
CSV_FILE = Path(__file__).resolve().parent / "data.csv"
CSV_FIELDS = ["timestamp", "area", "lux"]
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


def save_data(data):
    """Append one data; create CSV with a header if necessary."""
    with CSV_FILE.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        if file.tell() == 0:
            writer.writeheader()
        writer.writerow(data)


def load_data(area=None):
    """Read all data, optionally filtered by area."""
    if not CSV_FILE.exists():
        return []

    results = []
    with CSV_FILE.open("r", newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            row_area = int(row["area"])

            # Filter only if an area is specified
            if area is not None and row_area != area:
                continue

            results.append({
                "timestamp": row["timestamp"],
                "area": row_area,
                "lux": int(row["lux"]),
            })

    return results


@app.post("/api/light")
def upload_light():
    data = request.get_json()
    try:
        save_data(data)
    except OSError:
        app.logger.exception("Failed to save data")
        return jsonify({
            "error": "Could not save data"
            }), 500

    return "success", 201


@app.get("/api/light")
def get_light():
    area_text = request.args.get("area")

    if area_text is None:
        area = None  # No filter: retrieve all data

    try:
        data = load_data(area)
    except (OSError, ValueError, KeyError):
        app.logger.exception("Failed to read data")
        return jsonify({
            "error": "Could not read data"
            }), 500

    return jsonify({
        "count": len(data),
        "data": data
    }), 200


if __name__ == "__main__":
    print("IoT HTTP Server: http://127.0.0.1:5000")
    print("API: POST /api/light | GET /api/light?area=1")
    print("CSV:", CSV_FILE)
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=False)
