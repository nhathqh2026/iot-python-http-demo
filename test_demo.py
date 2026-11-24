"""Optional automated checks: python -m unittest -v test_demo.py"""

import csv
import tempfile
import unittest
from pathlib import Path

import server


class IoTHttpDemoTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.original_csv = server.CSV_FILE
        server.CSV_FILE = Path(self.temp.name) / "data.csv"
        self.client = server.app.test_client()

    def tearDown(self):
        server.CSV_FILE = self.original_csv
        self.temp.cleanup()

    def test_post_stores_csv_and_get_returns_data(self):
        post_response = self.client.post("/api/light", json={"timestamp": "2025-05-02 05:44:35", "area": 1, "lux": 500})
        self.assertEqual(post_response.status_code, 201)
        self.assertEqual(post_response.json["status"], "success")

        with server.CSV_FILE.open(newline="", encoding="utf-8") as file:
            rows = list(csv.DictReader(file))
        self.assertEqual(len(rows), 1)
        self.assertEqual(list(rows[0].keys()), ["timestamp", "area", "lux"])
        self.assertEqual(rows[0]["timestamp"], "2025-05-02 05:44:35")
        self.assertEqual(rows[0]["area"], "1")
        self.assertEqual(rows[0]["lux"], "500")

        get_response = self.client.get("/api/light?area=1")
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.json["count"], 1)
        self.assertEqual(get_response.json["measurements"][0]["lux"], 500)
        self.assertEqual(get_response.json["measurements"][0]["timestamp"], "2025-05-02 05:44:35")

    def test_get_unknown_area_returns_empty_list(self):
        response = self.client.get("/api/light?area=2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["measurements"], [])

    def test_invalid_post_returns_400_and_does_not_write(self):
        response = self.client.post("/api/light", json={"timestamp": "2025-05-02 05:44:35", "area": 1, "lux": -5})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(server.CSV_FILE.exists())

    def test_missing_timestamp_returns_400(self):
        response = self.client.post("/api/light", json={"area": 1, "lux": 500})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(server.CSV_FILE.exists())

    def test_invalid_timestamp_format_returns_400(self):
        for bad_time in ("2025-05-02T05:44:35", "2025-05-02 05:44",
                         "2025-02-30 05:44:35", "2025-5-2 5:4:3"):
            with self.subTest(timestamp=bad_time):
                response = self.client.post("/api/light", json={
                    "timestamp": bad_time, "area": 1, "lux": 500})
                self.assertEqual(response.status_code, 400)
        self.assertFalse(server.CSV_FILE.exists())

    def test_invalid_get_query_returns_400(self):
        response = self.client.get("/api/light?area=abc")
        self.assertEqual(response.status_code, 400)

    def test_non_json_post_returns_415(self):
        response = self.client.post("/api/light", data="area=1&lux=500")
        self.assertEqual(response.status_code, 415)


if __name__ == "__main__":
    unittest.main()
