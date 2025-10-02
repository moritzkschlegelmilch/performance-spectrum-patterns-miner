import unittest
from test_setup import client
import os
import env
import constants

import event_log_cache

class TestEventLogUpload(unittest.TestCase):

    def setUp(self) -> None:
        event_log_cache.cache.clear()

    @staticmethod
    def setup_uploaded_log(path, upload_name="simple-log.xes"):
        # Upload a valid event log file first
        filepath = os.path.join("resources", path)
        with open(filepath, "rb") as f:
            response = client.post(
                "/api/upload-event-log/",
                data={"name": "Test Log"},
                files={"file": (upload_name, f, 'application/xes')},
            )
        return response

    def test_upload_event_log(self):
        response = self.setup_uploaded_log("simple-log.xes")

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsInstance(data, dict)
        self.assertIn("id", data)
        self.assertEqual(data["name"], "Test Log")
        saved_file_path = f"{env.UPLOAD_DIR}/{data['path']}"
        self.assertTrue(os.path.isfile(saved_file_path), f"Uploaded file not found at {saved_file_path}")

    def test_upload_invalid_file(self):
        response = self.setup_uploaded_log("invalid-log.txt", upload_name='invalid-log.txt')

        self.assertEqual(response.status_code, 422)
        data = response.json()
        self.assertIn("detail", data)

    def test_get_event_log_choosing_data_success(self):
        data = self.setup_uploaded_log("simple-log.xes")
        event_log_id = data.json()["id"]
        # Call the endpoint that internally calls get_event_log_field_choosing_data
        response = client.get(f"/api/event-log/basic/{event_log_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['event_log']["column_count"], 18)
        self.assertEqual(data['event_log']["entry_count"], 12)
        self.assertIn("event_log", data)
        self.assertIn("df", data)
        self.assertIsInstance(data["df"], list)
        self.assertEqual(data["event_log"]["id"], event_log_id)
        self.assertEqual(12, len(data['df']))

    def test_get_event_log_choosing_data_to_few_columns(self):
        data = self.setup_uploaded_log("too_few_columns.xes")
        event_log_id = data.json()["id"]
        # Call the endpoint that internally calls get_event_log_field_choosing_data
        response = client.get(f"/api/event-log/basic/{event_log_id}")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"]["err"], constants.INVALID_EVENT_LOG_ERROR)
